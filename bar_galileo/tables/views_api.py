import json
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from django.db import transaction
from products.models import Producto
from .models import Mesa, Pedido, PedidoItem, Factura
from django.contrib.auth.models import User
from notifications.utils import notificar_usuario

# --- Helper Function ---

def _serialize_pedido(pedido):
    """Helper para convertir un objeto Pedido a un diccionario JSON."""
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

# --- API Views ---

def mesa_pedido_api(request, mesa_id):
    """API para obtener los datos de una mesa, su pedido activo y la lista de productos."""
    mesa = get_object_or_404(Mesa, id=mesa_id)
    pedido, created = Pedido.objects.get_or_create(mesa=mesa, estado='en_proceso')

    productos_data = []
    for p in Producto.objects.all().order_by('nombre'):
        first_image = p.imagenes.first()
        imagen_url = f"/static/{first_image.imagen}" if first_image else None
        productos_data.append({
            'id_producto': p.id_producto,
            'nombre': p.nombre,
            'precio_venta': p.precio_venta,
            'stock': p.stock,
            'imagen': imagen_url
        })

    return JsonResponse({
        'mesa': {'id': mesa.id, 'nombre': mesa.nombre},
        'pedido': _serialize_pedido(pedido),
        'productos': productos_data
    })

@transaction.atomic
def agregar_item_api(request):
    """API para agregar un item al pedido con validación de stock."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    data = json.loads(request.body)
    mesa = get_object_or_404(Mesa, id=data['mesa_id'])
    producto = get_object_or_404(Producto, id_producto=data['producto_id'])
    cantidad_a_agregar = data.get('cantidad', 1)

    pedido, created = Pedido.objects.get_or_create(mesa=mesa, estado='en_proceso')
    item, created_item = PedidoItem.objects.get_or_create(pedido=pedido, producto=producto, defaults={'precio_unitario': producto.precio_venta})

    cantidad_final = item.cantidad if not created_item else 0
    cantidad_final += cantidad_a_agregar

    if producto.stock < cantidad_final:
        error_msg = f"Stock insuficiente para {producto.nombre}. Disponible: {producto.stock}"
        return JsonResponse({'error': error_msg}, status=400)

    if not created_item:
        item.cantidad += cantidad_a_agregar
    else:
        item.cantidad = cantidad_a_agregar
    
    item.save()
    
    return JsonResponse({'pedido': _serialize_pedido(pedido)})

@transaction.atomic
def actualizar_item_api(request, item_id):
    """API para actualizar la cantidad de un item en el pedido con validación de stock."""
    if request.method != 'PATCH':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
        
    item = get_object_or_404(PedidoItem, id=item_id)
    data = json.loads(request.body)
    nueva_cantidad = data.get('cantidad')

    if nueva_cantidad is None or not isinstance(nueva_cantidad, int) or nueva_cantidad < 0:
        return JsonResponse({'error': 'Cantidad no válida'}, status=400)

    if item.producto.stock < nueva_cantidad:
        error_msg = f"Stock insuficiente para {item.producto.nombre}. Disponible: {item.producto.stock}"
        return JsonResponse({'error': error_msg}, status=400)

    if nueva_cantidad == 0:
        item.delete()
    else:
        item.cantidad = nueva_cantidad
        item.save()
    
    return JsonResponse({'pedido': _serialize_pedido(item.pedido)})

@transaction.atomic
def eliminar_item_api(request, item_id):
    """API para eliminar un item del pedido."""
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    item = get_object_or_404(PedidoItem, id=item_id)
    pedido = item.pedido
    item.delete()
    
    return JsonResponse({'pedido': _serialize_pedido(pedido)})

@transaction.atomic
def facturar_pedido_api(request, pedido_id):
    """API para facturar un pedido."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    with transaction.atomic():
        for item in pedido.items.all():
            producto = item.producto
            if producto.stock < item.cantidad:
                return JsonResponse({'error': f'No hay stock suficiente para "{producto.nombre}". Pedido no facturado.'}, status=400)
            
            producto.stock -= item.cantidad
            producto.save(update_fields=['stock'])

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