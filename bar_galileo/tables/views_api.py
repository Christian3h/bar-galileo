import json
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from django.db import transaction
from products.models import Producto
from .models import Mesa, Pedido, PedidoItem, Factura

def mesa_pedido_api(request, mesa_id):
    """API para obtener los datos de una mesa y su pedido activo"""
    mesa = get_object_or_404(Mesa, id=mesa_id)
    pedido = Pedido.objects.filter(mesa=mesa, estado='en_proceso').first()
    
    if not pedido:
        pedido = Pedido.objects.create(mesa=mesa)
    
    productos = Producto.objects.all().values('id_producto', 'nombre', 'precio_venta')
    
    return JsonResponse({
        'mesa': {
            'id': mesa.id,
            'nombre': mesa.nombre,
        },
        'pedido': {
            'id': pedido.id,
            'items': [
                {
                    'id': item.id,
                    'producto': {
                        'id': item.producto.id_producto,
                        'nombre': item.producto.nombre,
                    },
                    'cantidad': item.cantidad,
                    'precio_unitario': float(item.precio_unitario),
                    'subtotal': float(item.subtotal())
                }
                for item in pedido.items.select_related('producto')
            ],
            'total': float(pedido.total())
        },
        'productos': list(productos)
    })

@transaction.atomic
def agregar_item_api(request):
    """API para agregar un item al pedido"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    data = json.loads(request.body)
    mesa = get_object_or_404(Mesa, id=data['mesa_id'])
    producto = get_object_or_404(Producto, id_producto=data['producto_id'])
    
    pedido = Pedido.objects.filter(mesa=mesa, estado='en_proceso').first()
    if not pedido:
        pedido = Pedido.objects.create(mesa=mesa)
    
    item = PedidoItem.objects.filter(pedido=pedido, producto=producto).first()
    if item:
        item.cantidad += data.get('cantidad', 1)
        item.save()
    else:
        item = PedidoItem.objects.create(
            pedido=pedido,
            producto=producto,
            cantidad=data.get('cantidad', 1),
            precio_unitario=producto.precio_venta
        )
    
    return JsonResponse({
        'pedido': {
            'id': pedido.id,
            'items': [
                {
                    'id': item.id,
                    'producto': {
                        'id': item.producto.id_producto,
                        'nombre': item.producto.nombre,
                    },
                    'cantidad': item.cantidad,
                    'precio_unitario': float(item.precio_unitario),
                    'subtotal': float(item.subtotal())
                }
                for item in pedido.items.select_related('producto')
            ],
            'total': float(pedido.total())
        }
    })

@transaction.atomic
def eliminar_item_api(request, item_id):
    """API para eliminar un item del pedido"""
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    item = get_object_or_404(PedidoItem, id=item_id)
    pedido = item.pedido
    item.delete()
    
    return JsonResponse({
        'pedido': {
            'id': pedido.id,
            'items': [
                {
                    'id': item.id,
                    'producto': {
                        'id': item.producto.id_producto,
                        'nombre': item.producto.nombre,
                    },
                    'cantidad': item.cantidad,
                    'precio_unitario': float(item.precio_unitario),
                    'subtotal': float(item.subtotal())
                }
                for item in pedido.items.select_related('producto')
            ],
            'total': float(pedido.total())
        }
    })

@transaction.atomic
def facturar_pedido_api(request, pedido_id):
    """API para facturar un pedido"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    with transaction.atomic():
        # Actualizar el stock de los productos vendidos
        from products.models import Stock
        for item in pedido.items.all():
            producto = item.producto
            if producto.stock is not None:
                # Restar la cantidad vendida del stock
                nuevo_stock = max(0, producto.stock - item.cantidad)
                producto.stock = nuevo_stock
                producto.save()  # Esto automáticamente creará un registro en Stock
        
        # Crear la factura
        factura = Factura.objects.create(
            pedido=pedido,
            total=pedido.total()
        )
        
        # Actualizar el estado del pedido
        pedido.estado = 'facturado'
        pedido.save()
        
        # Liberar la mesa (solo si la mesa aún existe)
        if pedido.mesa:
            pedido.mesa.estado = 'disponible'
            pedido.mesa.save()
    
    return JsonResponse({
        'success': True,
        'factura_url': reverse('tables:ver_factura', args=[factura.id])
    })
