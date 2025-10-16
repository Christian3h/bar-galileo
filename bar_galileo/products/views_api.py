from django.http import JsonResponse
from .models import Proveedor, Marca, Categoria, ProductoImagen
from django.views.decorators.http import require_POST

@require_POST
def producto_imagen_eliminar_api(request, pk):
    try:
        imagen = ProductoImagen.objects.get(pk=pk)
        imagen.delete()
        return JsonResponse({'success': True})
    except ProductoImagen.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'La imagen no existe.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

def proveedores_json(request):
    proveedores = Proveedor.objects.all()
    data = []
    for proveedor in proveedores:
        data.append({
            'id': proveedor.id_proveedor,
            'proveedor': proveedor.nombre,  # Cambiado de 'nombre' a 'proveedor' para que coincida con la plantilla
            'direccion': proveedor.direccion,
            'telefono': proveedor.telefono,
            'email': proveedor.contacto,  # Usando contacto como email para la plantilla
        })
    return JsonResponse({'data': data})

def marcas_json(request):
    marcas = Marca.objects.all()
    data = []
    for marca in marcas:
        data.append({
            'id': marca.id_marca,
            'marca': marca.marca,
            'descripcion': marca.descripcion,
        })
    return JsonResponse({'data': data})

def categorias_json(request):
    categorias = Categoria.objects.all()
    data = []
    for categoria in categorias:
        data.append({
            'id': categoria.id_categoria,
            'nombre_categoria': categoria.nombre_categoria,
            'descripcion': categoria.descripcion,
        })
    return JsonResponse({'data': data})
