from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from datetime import datetime
from django.core.paginator import Paginator
from tables.models import Factura
from .models import FacturacionManager
from roles.decorators import permission_required
from django.contrib.auth.decorators import login_required
from decimal import InvalidOperation
import logging

logger = logging.getLogger(__name__)

@login_required
@permission_required('facturacion', 'ver')
def lista_facturas(request):
    """
    Vista para mostrar la lista de facturas con filtros de búsqueda
    """
    # Obtener parámetros de búsqueda
    busqueda = request.GET.get('busqueda', '')
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    
    # Convertir fechas si existen
    fecha_inicio_obj = None
    fecha_fin_obj = None
    
    if fecha_inicio:
        try:
            fecha_inicio_obj = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        except ValueError:
            pass
    
    if fecha_fin:
        try:
            fecha_fin_obj = datetime.strptime(fecha_fin, '%Y-%m-%d')
        except ValueError:
            pass
    
    try:
        # Obtener facturas usando el nuevo manager
        facturas = FacturacionManager.obtener_facturas_con_filtros(
            busqueda=busqueda,
            fecha_inicio=fecha_inicio_obj,
            fecha_fin=fecha_fin_obj
        )
        
        # Paginación
        paginator = Paginator(facturas, 10)  # 10 facturas por página
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Estadísticas
        estadisticas = FacturacionManager.obtener_estadisticas()
        
    except Exception as e:
        logger.error(f"Error en lista_facturas: {e}")
        messages.error(request, f"Error cargando facturas: {e}")
        page_obj = Paginator([], 10).get_page(1)
        estadisticas = {
            'total_facturas': 0,
            'total_ingresos': 0,
            'facturas_hoy': 0,
            'ingresos_hoy': 0,
        }
    
    context = {
        'page_obj': page_obj,
        'busqueda': busqueda,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'estadisticas': estadisticas,
    }
    
    return render(request, 'facturacion/lista_facturas.html', context)

@login_required
@permission_required('facturacion', 'ver')
def detalle_factura(request, factura_id):
    """
    Vista para mostrar el detalle de una factura específica
    """
    factura = FacturacionManager.obtener_factura_por_id(factura_id)
    
    if not factura:
        messages.error(request, 'Factura no encontrada.')
        return redirect('facturacion:lista_facturas')
    
    context = {
        'factura': factura,
    }
    
    return render(request, 'facturacion/detalle_factura.html', context)

@login_required
@permission_required('facturacion', 'eliminar')
def eliminar_factura(request, factura_id):
    """
    Vista para eliminar una factura
    """
    factura = get_object_or_404(Factura, id=factura_id)
    
    if request.method == 'POST':
        numero_factura = factura.numero
        factura.delete()
        messages.success(request, f'Factura #{numero_factura} eliminada exitosamente.')
        return redirect('facturacion:lista_facturas')
    
    context = {
        'factura': factura,
    }
    
    return render(request, 'facturacion/confirmar_eliminar.html', context)

@login_required
@permission_required('facturacion', 'ver')
def buscar_facturas_ajax(request):
    """
    Vista AJAX para búsqueda de facturas en tiempo real
    """
    if request.method == 'GET':
        busqueda = request.GET.get('busqueda', '')
        
        facturas = FacturacionManager.obtener_facturas_con_filtros(busqueda=busqueda)[:10]
        
        resultados = []
        for factura in facturas:
            resultados.append({
                'id': factura.id,
                'numero': factura.numero,
                'fecha': factura.fecha.strftime('%d/%m/%Y %H:%M'),
                'mesa': factura.pedido.mesa.nombre if factura.pedido.mesa else 'Sin mesa',
                'total': str(factura.total),
            })
        
        return JsonResponse({'facturas': resultados})
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)
