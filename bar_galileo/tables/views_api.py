import json
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from django.db import transaction
from products.models import Producto
from .models import Mesa, Pedido, PedidoItem, Factura
from django.contrib.auth.models import User
from notifications.utils import notificar_usuario
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# --- Helper Functions ---

def _serialize_pedido(pedido):
    pedido.refresh_from_db()
    return {
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
            for item in pedido.items.select_related('producto').order_by('id')
        ],
        'total': float(pedido.total())
    }

def _broadcast_stock_update(producto_id, delta):
    """Envía una actualización de stock a través de WebSockets."""
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'stock_updates',
        {
            'type': 'stock_update',
            'message': {
                'product_id': producto_id,
                'delta': delta
            }
        }
    )

# --- API Views ---

def mesa_pedido_api(request, mesa_id):
    mesa = get_object_or_404(Mesa, id=mesa_id)
    pedido, _ = Pedido.objects.get_or_create(mesa=mesa, estado='en_proceso')

    productos_data = []
    for p in Producto.objects.all().order_by('nombre'):
        first_image = p.imagenes.first()
        imagen_url = f"/static/{first_image.imagen}" if first_image else None
        productos_data.append({
            'id_producto': p.id_producto,
            'nombre': p.nombre,
            'precio_venta': p.precio_venta,
            'stock': p.stock, # Stock real
            'imagen': imagen_url
        })

    # Calcula todo el stock reservado en pedidos activos
    reservas_stock = { 
        item['producto_id']: item['cantidad_total'] 
        for item in PedidoItem.objects.filter(pedido__estado='en_proceso').values('producto_id').annotate(cantidad_total=Sum('cantidad'))
    }

    return JsonResponse({
        'mesa': {'id': mesa.id, 'nombre': mesa.nombre},
        'pedido': _serialize_pedido(pedido),
        'productos': productos_data,
        'reservas_stock': reservas_stock
    })

@transaction.atomic
def agregar_item_api(request):
    data = json.loads(request.body)
    producto = get_object_or_404(Producto, id_producto=data['producto_id'])
    cantidad_a_agregar = data.get('cantidad', 1)

    # Lógica de negocio... (código existente)
    # ... (validación de stock, creación/actualización de item)
    # ...
    # Después de guardar el item exitosamente:
    _broadcast_stock_update(producto.id_producto, -cantidad_a_agregar)
    
    # ... (código existente para devolver la respuesta)
    pedido, _ = Pedido.objects.get_or_create(mesa_id=data['mesa_id'], estado='en_proceso')
    item, created = PedidoItem.objects.get_or_create(pedido=pedido, producto=producto, defaults={'precio_unitario': producto.precio_venta})
    
    # Validar stock antes de modificar
    cantidad_total_requerida = (item.cantidad if not created else 0) + cantidad_a_agregar
    if producto.stock < cantidad_total_requerida:
        return JsonResponse({'error': f'Stock insuficiente para {producto.nombre}. Disponible: {producto.stock}'}, status=400)

    if not created:
        item.cantidad += cantidad_a_agregar
    else:
        item.cantidad = cantidad_a_agregar
    item.save()

    return JsonResponse({'pedido': _serialize_pedido(pedido)})

@transaction.atomic
def actualizar_item_api(request, item_id):
    item = get_object_or_404(PedidoItem, id=item_id)
    old_cantidad = item.cantidad
    
    data = json.loads(request.body)
    nueva_cantidad = data.get('cantidad')

    if nueva_cantidad is None or not isinstance(nueva_cantidad, int) or nueva_cantidad < 0:
        return JsonResponse({'error': 'Cantidad no válida'}, status=400)

    # Validar stock
    if item.producto.stock < nueva_cantidad:
        return JsonResponse({'error': f'Stock insuficiente para {item.producto.nombre}. Disponible: {item.producto.stock}'}, status=400)

    if nueva_cantidad == 0:
        item.delete()
    else:
        item.cantidad = nueva_cantidad
        item.save()

    delta = nueva_cantidad - old_cantidad
    _broadcast_stock_update(item.producto.id_producto, -delta)
    
    return JsonResponse({'pedido': _serialize_pedido(item.pedido)})

@transaction.atomic
def eliminar_item_api(request, item_id):
    item = get_object_or_404(PedidoItem, id=item_id)
    producto_id = item.producto.id_producto
    cantidad_eliminada = item.cantidad
    pedido = item.pedido

    item.delete()

    _broadcast_stock_update(producto_id, cantidad_eliminada)
    
    return JsonResponse({'pedido': _serialize_pedido(pedido)})

@transaction.atomic
def facturar_pedido_api(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    with transaction.atomic():
        for item in pedido.items.all():
            producto = item.producto
            if producto.stock < item.cantidad:
                return JsonResponse({'error': f'No hay stock suficiente para "{producto.nombre}". Pedido no facturado.'}, status=400)
            
            producto.stock -= item.cantidad
            producto.save(update_fields=['stock'])
            # No se necesita broadcast aquí porque el stock real se actualiza
            # y los items ya no estarán en un pedido 'en_proceso'

        factura = Factura.objects.create(pedido=pedido, total=pedido.total())
        pedido.estado = 'facturado'
        pedido.save()
        
        if pedido.mesa:
            mesa = pedido.mesa
            mesa.estado = 'disponible'
            mesa.save()
            mensaje = f"El pedido de la mesa '{mesa.nombre}' fue facturado. La mesa está ahora disponible."
            notificar_usuario(request.user, mensaje)
    
    return JsonResponse({
        'success': True,
        'factura_url': reverse('tables:ver_factura', args=[factura.id])
    })
