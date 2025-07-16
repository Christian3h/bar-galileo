from django.http import JsonResponse
from .models import Proveedor, Marca, Categoria



def proveedores_json(request):
    proveedores = Proveedor.objects.all()
    data = []
    for proveedor in proveedores:
        data.append({
            'id': proveedor.id_proveedor,
            'nombre': proveedor.nombre,
            'contacto': proveedor.contacto,
            'telefono': proveedor.telefono,
            'direccion': proveedor.direccion,
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
