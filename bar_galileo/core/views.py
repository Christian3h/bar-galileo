from django.shortcuts import render
from django.http import JsonResponse
from django.template.loader import render_to_string
from products.models import Producto
from django.views.generic import ListView
from django.views import View

# Create your views here.

class indexView(ListView): 
    model = Producto
    template_name = 'index.html'
    context_object_name = 'productos'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener solo los primeros 3 productos para mostrar inicialmente
        context['productos_iniciales'] = Producto.objects.all()[:3]
        context['total_productos'] = Producto.objects.count()
        return context

class ProductosAjaxView(View):
    def get(self, request):
        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 6))
        
        productos = Producto.objects.all()[offset:offset + limit]
        total_productos = Producto.objects.count()
        
        productos_data = []
        for producto in productos:
            # Obtener la primera imagen del producto
            imagen_url = None
            if producto.imagenes.exists():
                primera_imagen = producto.imagenes.first()
                imagen_url = f"/static/{primera_imagen.imagen}"
            
            productos_data.append({
                'id': producto.id_producto,
                'nombre': producto.nombre,
                'precio': str(producto.precio_venta),
                'descripcion': producto.descripcion,
                'imagen_url': imagen_url,
            })
        
        return JsonResponse({
            'productos': productos_data,
            'has_more': (offset + limit) < total_productos,
            'total': total_productos
        })