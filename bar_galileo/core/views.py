from django.shortcuts import render
from django.http import JsonResponse
from django.template.loader import render_to_string
from products.models import Producto, Categoria, Marca
from django.views.generic import ListView
from django.views import View
from django.db.models import Q

# Create your views here.

class indexView(ListView):
    model = Producto
    template_name = 'index.html'
    context_object_name = 'productos'

    def get_queryset(self):
        return Producto.objects.filter(activo=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['productos_iniciales'] = Producto.objects.filter(activo=True)[:3]
        context['total_productos'] = Producto.objects.filter(activo=True).count()
        
        # Agregar imágenes del carrusel desde la base de datos
        try:
            from site_images.models import CarouselImage, SiteImage, SiteImageSection, SiteContent
            context['carousel_images'] = CarouselImage.objects.filter(is_active=True).order_by('order')

            # Agregar imagen de la sección "About" si existe
            try:
                about_section = SiteImageSection.objects.get(section_type='about')
                about_images = SiteImage.objects.filter(section=about_section, is_active=True)
                if about_images.exists():
                    context['about_image'] = about_images.first()
            except SiteImageSection.DoesNotExist:
                pass

            # Cargar contenido editable de cada sección de la home
            from site_images.views import SECTIONS_DEFAULT
            for section_key, defaults in SECTIONS_DEFAULT.items():
                obj, _ = SiteContent.objects.get_or_create(section=section_key, defaults=defaults)
                context[f'content_{section_key}'] = obj

        except Exception:
            # Si aún no existen las tablas (antes de migrar), continuar sin error
            pass
        
        return context

class ProductosAjaxView(View):
    def get(self, request):
        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 6))

        qs = Producto.objects.filter(activo=True)
        productos = qs.order_by('nombre')[offset:offset + limit]
        total_productos = qs.count()

        productos_data = []
        for producto in productos:
            imagen_url = None
            if producto.imagenes.exists():
                primera_imagen = producto.imagenes.first()
                imagen_url = f"/media/{primera_imagen.imagen}"

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

class StoreView(ListView):
    model = Producto
    template_name = 'store/store.html'
    context_object_name = 'productos'
    paginate_by = 9

    def get_queryset(self):
        queryset = Producto.objects.filter(activo=True).order_by('nombre')
        categoria = self.request.GET.get('categoria')
        marca = self.request.GET.get('marca')
        min_precio = self.request.GET.get('min_precio')
        max_precio = self.request.GET.get('max_precio')

        if categoria:
            queryset = queryset.filter(id_categoria__nombre_categoria=categoria)

        if marca:
            queryset = queryset.filter(id_marca__marca=marca)

        if min_precio and max_precio:
            queryset = queryset.filter(precio_venta__range=(min_precio, max_precio))
        elif min_precio:
            queryset = queryset.filter(precio_venta__gte=min_precio)
        elif max_precio:
            queryset = queryset.filter(precio_venta__lte=max_precio)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = Categoria.objects.all()
        context['marcas'] = Marca.objects.all()
        context['categoria_actual'] = self.request.GET.get('categoria', '')
        context['marca_actual'] = self.request.GET.get('marca', '')
        context['min_precio_actual'] = self.request.GET.get('min_precio', '')
        context['max_precio_actual'] = self.request.GET.get('max_precio', '')
        return context
