"""
Vistas del módulo de reportes.

Expone el CRUD completo del modelo `Reporte` más dos acciones especiales:
  - `exportar_reporte`      : descarga el reporte en PDF, Excel o CSV.
  - `generar_reporte_datos` : recalcula y guarda los datos en caché (AJAX).

Control de acceso
-----------------
Todas las vistas están protegidas por el decorador `permission_required`
del módulo `roles`. Los permisos necesarios son:
  - 'ver'      : listar, ver detalle, exportar y generar datos.
  - 'crear'    : crear nuevos reportes.
  - 'editar'   : modificar reportes existentes.
  - 'eliminar' : borrar reportes.

El módulo de lógica de negocio (consultas y exportación) vive en `utils.py`.
Las vistas son únicamente responsables de la capa HTTP (recibir request,
coordinar llamadas a utils, devolver response y mensajes flash).
"""

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


@method_decorator(permission_required('reportes', 'ver'), name='dispatch')
class ReporteListView(ListView):
    # Lista todos los reportes. Soporta filtros por tipo, periodo, usuario y búsqueda de texto (GET).
    # DataTables pagina en cliente, por eso paginate_by=None.
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
    # Muestra el detalle del reporte. Inyecta datos_json deserializado al contexto.
    model = Reporte
    template_name = 'reportes/reporte_detail.html'
    context_object_name = 'reporte'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener datos del reporte si están disponibles
        datos = self.object.get_datos()
        context['datos_reporte'] = datos
        context['tiene_datos'] = bool(datos)
        
        return context


@method_decorator(permission_required('reportes', 'crear'), name='dispatch')
class ReporteCreateView(SuccessMessageMixin, CreateView):
    # Crea un nuevo reporte. Asigna creado_por al usuario actual automáticamente.
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
    # Edita un reporte existente. Si se cambian fechas o tipo, los datos en caché quedarán desactualizados.
    model = Reporte
    form_class = ReporteForm
    template_name = 'reportes/reporte_form.html'
    success_url = reverse_lazy('reportes:reporte_list')
    success_message = "Reporte actualizado exitosamente"


@method_decorator(permission_required('reportes', 'eliminar'), name='dispatch')
class ReporteDeleteView(SuccessMessageMixin, DeleteView):
    # Elimina el reporte de la BD. El archivo adjunto en disco NO se borra automáticamente.
    model = Reporte
    template_name = 'reportes/reporte_confirm_delete.html'
    success_url = reverse_lazy('reportes:reporte_list')
    success_message = "Reporte eliminado exitosamente"
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


@permission_required('reportes', 'ver')
def exportar_reporte(request, pk, formato):
    # Descarga el reporte como archivo. Si no hay datos en caché los genera primero.
    # formato puede ser: 'pdf', 'excel' o 'csv'. Llama a la función correspondiente en utils.py.
    from .utils import generar_pdf_reporte, generar_excel_reporte, generar_csv_reporte, obtener_datos_reporte_detallado
    import traceback
    
    # Verificar que el usuario esté autenticado
    if not request.user.is_authenticated:
        messages.error(request, "Debes iniciar sesión para exportar reportes")
        return redirect('accounts:login')
    
    reporte = get_object_or_404(Reporte, pk=pk)
    
    try:
        # Obtener o regenerar datos del reporte
        datos = reporte.get_datos()
        
        # Si no hay datos o están vacíos, generarlos
        if not datos or not datos.get('resumen'):
            print(f"Generando datos para reporte {reporte.id}...")
            datos = obtener_datos_reporte_detallado(reporte)
            reporte.set_datos(datos)
            reporte.generado = True
            reporte.save()
            print(f"Datos generados: {len(datos.get('detalles', []))} detalles")
        
        # Validar formato
        if formato not in ['pdf', 'excel', 'csv']:
            messages.error(request, f"Formato de exportación no válido: {formato}")
            return redirect('reportes:reporte_detail', pk=pk)
        
        # Exportar según formato
        if formato == 'pdf':
            return generar_pdf_reporte(reporte, datos)
        elif formato == 'excel':
            return generar_excel_reporte(reporte, datos)
        elif formato == 'csv':
            return generar_csv_reporte(reporte, datos)
            
    except Exception as e:
        error_msg = f"Error al exportar reporte: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        messages.error(request, error_msg)
        return redirect('reportes:reporte_detail', pk=pk)


@permission_required('reportes', 'ver')
def generar_reporte_datos(request, pk):
    # Endpoint AJAX. Genera/actualiza los datos del reporte y devuelve JSON con el resumen.
    from .utils import obtener_datos_reporte_detallado
    
    # Verificar que el usuario esté autenticado
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'Debes iniciar sesión'
        }, status=401)
    
    reporte = get_object_or_404(Reporte, pk=pk)
    
    try:
        # Generar datos según el tipo de reporte
        datos_generados = obtener_datos_reporte_detallado(reporte)
        
        # Guardar datos en el reporte
        reporte.set_datos(datos_generados)
        reporte.generado = True
        reporte.save()
        
        messages.success(request, f"Reporte '{reporte.nombre}' generado exitosamente")
        
        # Preparar respuesta con resumen
        return JsonResponse({
            'success': True,
            'message': 'Reporte generado correctamente',
            'resumen': datos_generados.get('resumen', {}),
            'cantidad_detalles': len(datos_generados.get('detalles', [])),
            'totales': datos_generados.get('totales', {})
        })
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        messages.error(request, f"Error al generar reporte: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}',
            'detail': error_detail
        }, status=500)



