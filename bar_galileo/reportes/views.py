from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q, Count
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from roles.decorators import permission_required
from .models import Reporte
from .forms import ReporteForm, ReporteFilterForm
from .utils import generar_pdf_reporte, generar_excel_reporte, generar_csv_reporte


@method_decorator(permission_required('reportes', 'ver'), name='dispatch')
class ReporteListView(ListView):
    """Vista para listar todos los reportes"""
    model = Reporte
    template_name = 'reportes/reporte_list.html'
    context_object_name = 'reportes'
    # Evitar paginación del lado servidor porque DataTables ya pagina en cliente
    paginate_by = None
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por tipo
        tipo = self.request.GET.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        # Filtrar por periodo
        periodo = self.request.GET.get('periodo')
        if periodo:
            queryset = queryset.filter(periodo=periodo)
        
        # Filtrar por usuario creador
        usuario = self.request.GET.get('usuario')
        if usuario:
            queryset = queryset.filter(creado_por__id=usuario)
        
        # Búsqueda por nombre o descripción
        busqueda = self.request.GET.get('busqueda')
        if busqueda:
            queryset = queryset.filter(
                Q(nombre__icontains=busqueda) | 
                Q(descripcion__icontains=busqueda)
            )
        
        return queryset.select_related('creado_por')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas
        context['total_reportes'] = Reporte.objects.count()
        context['reportes_por_tipo'] = Reporte.objects.values('tipo').annotate(
            total=Count('id')
        ).order_by('-total')
        
        # Formulario de filtros
        context['filter_form'] = ReporteFilterForm(self.request.GET or None)
        
        return context


@method_decorator(permission_required('reportes', 'ver'), name='dispatch')
class ReporteDetailView(DetailView):
    """Vista de detalle de un reporte"""
    model = Reporte
    template_name = 'reportes/reporte_detail.html'
    context_object_name = 'reporte'


@method_decorator(permission_required('reportes', 'crear'), name='dispatch')
class ReporteCreateView(SuccessMessageMixin, CreateView):
    """Vista para crear un nuevo reporte"""
    model = Reporte
    form_class = ReporteForm
    template_name = 'reportes/reporte_form.html'
    success_url = reverse_lazy('reportes:reporte_list')
    success_message = "Reporte creado exitosamente"
    
    def form_valid(self, form):
        form.instance.creado_por = self.request.user
        return super().form_valid(form)


@method_decorator(permission_required('reportes', 'editar'), name='dispatch')
class ReporteUpdateView(SuccessMessageMixin, UpdateView):
    """Vista para editar un reporte existente"""
    model = Reporte
    form_class = ReporteForm
    template_name = 'reportes/reporte_form.html'
    success_url = reverse_lazy('reportes:reporte_list')
    success_message = "Reporte actualizado exitosamente"


@method_decorator(permission_required('reportes', 'eliminar'), name='dispatch')
class ReporteDeleteView(SuccessMessageMixin, DeleteView):
    """Vista para eliminar un reporte"""
    model = Reporte
    template_name = 'reportes/reporte_confirm_delete.html'
    success_url = reverse_lazy('reportes:reporte_list')
    success_message = "Reporte eliminado exitosamente"
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


@permission_required('reportes', 'exportar')
def exportar_reporte(request, pk, formato):
    """Vista para exportar un reporte en diferentes formatos"""
    reporte = get_object_or_404(Reporte, pk=pk)
    
    # Obtener datos del reporte según su tipo
    datos = obtener_datos_reporte(reporte)
    
    if formato == 'pdf':
        return generar_pdf_reporte(reporte, datos)
    elif formato == 'excel':
        return generar_excel_reporte(reporte, datos)
    elif formato == 'csv':
        return generar_csv_reporte(reporte, datos)
    else:
        messages.error(request, "Formato de exportación no válido")
        return redirect('reportes:reporte_detail', pk=pk)


@permission_required('reportes', 'generar')
def generar_reporte_datos(request, pk):
    """Vista para generar/actualizar datos del reporte"""
    reporte = get_object_or_404(Reporte, pk=pk)
    
    try:
        # Generar datos según el tipo de reporte
        datos_generados = procesar_datos_reporte(reporte)
        
        # Marcar como generado
        reporte.generado = True
        reporte.save()
        
        messages.success(request, f"Reporte '{reporte.nombre}' generado exitosamente")
        return JsonResponse({
            'success': True,
            'message': 'Reporte generado correctamente',
            'datos': datos_generados
        })
    except Exception as e:
        messages.error(request, f"Error al generar reporte: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)


def obtener_datos_reporte(reporte):
    """Obtiene los datos del reporte según su tipo"""
    from django.db.models import Sum, Count, Avg
    from datetime import datetime
    
    datos = {}
    
    if reporte.tipo == 'ventas':
        # Importar modelos necesarios
        try:
            from facturacion.models import Factura
            
            facturas = Factura.objects.filter(
                fecha__range=[reporte.fecha_inicio, reporte.fecha_fin]
            )
            
            datos = {
                'Total de Ventas': facturas.aggregate(Sum('total'))['total__sum'] or 0,
                'Cantidad de Facturas': facturas.count(),
                'Promedio por Factura': facturas.aggregate(Avg('total'))['total__avg'] or 0,
            }
        except ImportError:
            datos = {'mensaje': 'Módulo de facturación no disponible'}
    
    elif reporte.tipo == 'gastos':
        try:
            from expenses.models import Expense
            
            gastos = Expense.objects.filter(
                date__range=[reporte.fecha_inicio, reporte.fecha_fin]
            )
            
            datos = {
                'Total de Gastos': gastos.aggregate(Sum('amount'))['amount__sum'] or 0,
                'Cantidad de Gastos': gastos.count(),
                'Promedio por Gasto': gastos.aggregate(Avg('amount'))['amount__avg'] or 0,
            }
        except ImportError:
            datos = {'mensaje': 'Módulo de gastos no disponible'}
    
    elif reporte.tipo == 'nominas':
        try:
            from nominas.models import Payroll
            
            nominas = Payroll.objects.filter(
                start_date__gte=reporte.fecha_inicio,
                end_date__lte=reporte.fecha_fin
            )
            
            datos = {
                'Total Nóminas': nominas.aggregate(Sum('net_salary'))['net_salary__sum'] or 0,
                'Cantidad de Nóminas': nominas.count(),
                'Promedio por Nómina': nominas.aggregate(Avg('net_salary'))['net_salary__avg'] or 0,
            }
        except ImportError:
            datos = {'mensaje': 'Módulo de nóminas no disponible'}
    
    elif reporte.tipo == 'inventario':
        try:
            from products.models import Product
            
            productos = Product.objects.all()
            
            datos = {
                'Total de Productos': productos.count(),
                'Productos con Stock Bajo': productos.filter(stock__lt=10).count(),
            }
        except ImportError:
            datos = {'mensaje': 'Módulo de productos no disponible'}
    
    else:  # general
        datos = {
            'Periodo': f"{reporte.fecha_inicio.strftime('%d/%m/%Y')} - {reporte.fecha_fin.strftime('%d/%m/%Y')}",
            'Duración': f"{reporte.duracion_dias} días",
        }
    
    return datos


def procesar_datos_reporte(reporte):
    """Procesa y genera los datos del reporte"""
    datos = obtener_datos_reporte(reporte)
    
    # Aquí puedes agregar lógica adicional de procesamiento
    # como cálculos, análisis, etc.
    
    return datos
