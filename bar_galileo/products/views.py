# Vistas públicas y de autenticación para la aplicación Bar Galileo
#
# Este archivo contiene las vistas principales del sistema, incluyendo:
# - Vistas públicas (inicio, nosotros, menú, reservas)
# - Autenticación de usuarios (login, logout, registro)
# - CRUD de productos (listar, agregar, editar, eliminar)
#
# Cada clase y método está documentado para facilitar el mantenimiento y la extensión del sistema.

from django.views.generic import TemplateView, View, UpdateView, DeleteView, CreateView
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from .models import Categoria, Producto, Proveedor, Marca, ProductoImagen, procesar_y_guardar_imagen, Stock
from .forms import ProductoForm, CategoriaForm, ProveedorForm, MarcaForm
import os
import logging
from roles.decorators import permission_required
from django.utils.decorators import method_decorator

logger = logging.getLogger(__name__)

class ProductosJsonView(View):
    def get(self, request):
        productos = Producto.objects.select_related('id_categoria', 'id_proveedor', 'id_marca').prefetch_related('imagenes', 'stocks').all()
        data = []
        for producto in productos:
            primera_imagen = producto.imagenes.first()
            imagen_url = request.build_absolute_uri(f'/static/{primera_imagen.imagen}') if primera_imagen else ''
            
            # Obtener el stock actual de la tabla Stock
            ultimo_stock = producto.stocks.order_by('-fecha_hora').first()
            stock_actual = ultimo_stock.cantidad if ultimo_stock else (producto.stock or 0)
            
            data.append({
                'id': producto.id_producto,
                'nombre': producto.nombre,
                'precio_compra': str(producto.precio_compra or ''),
                'precio_venta': str(producto.precio_venta or ''),
                'stock': producto.stock or 0,
                'stock_actual': stock_actual,
                'descripcion': producto.descripcion or '',
                'categoria': producto.id_categoria.nombre_categoria if producto.id_categoria else '',
                'proveedor': producto.id_proveedor.nombre if producto.id_proveedor else '',
                'marca': producto.id_marca.marca if producto.id_marca else '',
                'imagen_url': imagen_url,
            })
        return JsonResponse({'data': data})


    
class ProductosView(TemplateView):
    template_name = "productos.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["productos"] = Producto.objects.all()
        context["form"] = ProductoForm()
        return context

    def post(self, request, *args, **kwargs):
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto = form.save()
            for index, imagen in enumerate(request.FILES.getlist('imagenes')):
                ruta = procesar_y_guardar_imagen(imagen, producto.id_producto, f"{producto.id_producto}_{index}")
                ProductoImagen.objects.create(producto=producto, imagen=ruta)
            messages.success(request, "Producto agregado correctamente.")
            return redirect("products:productos")
        context = self.get_context_data()
        context["form"] = form
        return self.render_to_response(context)


class ProductoUpdateView(UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = "productos_form.html"
    success_url = reverse_lazy("products:productos")
    pk_url_kwarg = "pk"

    def get_object(self, queryset=None):
        return Producto.objects.get(id_producto=self.kwargs.get(self.pk_url_kwarg))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["imagenes"] = ProductoImagen.objects.filter(producto=self.object)
        return context

    def form_valid(self, form):
        producto = form.save()

        # Obtener el índice más alto de las imágenes actuales
        imagenes_existentes = ProductoImagen.objects.filter(producto=producto).values_list('imagen', flat=True)
        indices = []
        for ruta in imagenes_existentes:
            # Extraer el número después del guión bajo "_"
            nombre_archivo = os.path.basename(ruta)  # ej: 1_0.webp
            try:
                indice = int(nombre_archivo.split('_')[-1].split('.')[0])
                indices.append(indice)
            except (IndexError, ValueError):
                continue

        siguiente_indice = max(indices) + 1 if indices else 0

        # Guardar nuevas imágenes con índice correcto
        for imagen in self.request.FILES.getlist('imagenes'):
            ruta = procesar_y_guardar_imagen(imagen, producto.id_producto, f"{producto.id_producto}_{siguiente_indice}")
            ProductoImagen.objects.create(producto=producto, imagen=ruta)
            siguiente_indice += 1  # incrementar para la siguiente imagen

        messages.success(self.request, "Producto actualizado correctamente.")
        return super().form_valid(form)


class ProductoDeleteView(DeleteView):
    model = Producto
    template_name = "productos_confirm_delete.html"
    success_url = reverse_lazy("products:productos")
    pk_url_kwarg = "pk"

    def get_object(self, queryset=None):
        return Producto.objects.get(id_producto=self.kwargs.get(self.pk_url_kwarg))

    def delete(self, request, *args, **kwargs):
        producto = self.get_object()
        imagenes = ProductoImagen.objects.filter(producto=producto)
        for imagen in imagenes:
            path = os.path.join(settings.BASE_DIR, 'static', imagen.imagen)
            if os.path.exists(path):
                os.remove(path)
        imagenes.delete()
        producto.delete()
        messages.success(request, "Producto eliminado correctamente.")
        return redirect(self.success_url)


class CategoriaListView(TemplateView):
    """
    Vista para mostrar la lista de categorías.
    """
    template_name = "categorias.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categorias"] = Categoria.objects.all()
        return context

class CategoriasView(TemplateView):
    """
    Vista principal para el CRUD de categorías: muestra la lista y el formulario de alta.
    """
    template_name = "categorias.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categorias"] = Categoria.objects.all()
        context["form"] = CategoriaForm()
        return context

    def post(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Manejar petición AJAX
            try:
                form = CategoriaForm(request.POST)
                if form.is_valid():
                    categoria = form.save()
                    return JsonResponse({
                        'success': True, 
                        'message': 'Categoría agregada correctamente.',
                        'data': {
                            'id': categoria.id_categoria,
                            'nombre_categoria': categoria.nombre_categoria,
                            'descripcion': categoria.descripcion
                        }
                    })
                else:
                    errors = dict(form.errors.items())
                    error_messages = []
                    for field, field_errors in errors.items():
                        for error in field_errors:
                            error_messages.append(f"{field}: {error}")
                    return JsonResponse({
                        'success': False, 
                        'error': '; '.join(error_messages),
                        'errors': errors
                    }, status=400)
            except Exception as e:
                logger.error(f"Error en CategoriasView POST AJAX: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'error': f'Error interno del servidor: {str(e)}'
                }, status=500)
        else:
            # Manejar petición normal
            form = CategoriaForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Categoría agregada correctamente.")
                return redirect("products:categorias")
            context = self.get_context_data(**kwargs)
            context["form"] = form
            return self.render_to_response(context)

class CategoriaUpdateView(UpdateView):
    """
    Vista para editar una categoría existente.
    """
    model = Categoria
    form_class = CategoriaForm
    template_name = "categorias_form.html"
    success_url = reverse_lazy("products:categorias")
    pk_url_kwarg = "pk"
    lookup_field = "id_categoria"

    def get_object(self, queryset=None):
        return self.model.objects.get(id_categoria=self.kwargs.get(self.pk_url_kwarg))

    def form_valid(self, form):
        messages.success(self.request, "Categoría actualizada correctamente.")
        return super().form_valid(form)

class CategoriaDeleteView(DeleteView):
    """
    Vista para eliminar una categoría existente.
    """
    model = Categoria
    template_name = "categorias_confirm_delete.html"
    success_url = reverse_lazy("products:categorias")
    pk_url_kwarg = "pk"
    lookup_field = "id_categoria"

    def get_object(self, queryset=None):
        return self.model.objects.get(id_categoria=self.kwargs.get(self.pk_url_kwarg))

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Categoría eliminada correctamente.")
        return super().delete(request, *args, **kwargs)

class ProveedoresView(TemplateView):
    """
    Vista principal para el CRUD de proveedores: muestra la lista y el formulario de alta.
    """
    template_name = "proveedores.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["proveedores"] = Proveedor.objects.all()
        context["form"] = ProveedorForm()
        return context

    def post(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Manejar petición AJAX
            try:
                form = ProveedorForm(request.POST)
                if form.is_valid():
                    proveedor = form.save()
                    return JsonResponse({
                        'success': True, 
                        'message': 'Proveedor agregado correctamente.',
                        'data': {
                            'id': proveedor.id_proveedor,
                            'nombre': proveedor.nombre,
                            'contacto': proveedor.contacto,
                            'telefono': proveedor.telefono,
                            'direccion': proveedor.direccion
                        }
                    })
                else:
                    errors = dict(form.errors.items())
                    error_messages = []
                    for field, field_errors in errors.items():
                        for error in field_errors:
                            error_messages.append(f"{field}: {error}")
                    return JsonResponse({
                        'success': False, 
                        'error': '; '.join(error_messages),
                        'errors': errors
                    }, status=400)
            except Exception as e:
                logger.error(f"Error en ProveedoresView POST AJAX: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'error': f'Error interno del servidor: {str(e)}'
                }, status=500)
        else:
            # Manejar petición normal
            form = ProveedorForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Proveedor agregado correctamente.")
                return redirect("products:proveedores")
            context = self.get_context_data(**kwargs)
            context["form"] = form
            return self.render_to_response(context)

class ProveedorUpdateView(UpdateView):
    """
    Vista para editar un proveedor existente.
    """
    model = Proveedor
    form_class = ProveedorForm
    template_name = "proveedores_form.html"
    success_url = reverse_lazy("products:proveedores")
    pk_url_kwarg = "pk"
    lookup_field = "id_proveedor"

    def get_object(self, queryset=None):
        return self.model.objects.get(id_proveedor=self.kwargs.get(self.pk_url_kwarg))

    def form_valid(self, form):
        messages.success(self.request, "Proveedor actualizado correctamente.")
        return super().form_valid(form)

class ProveedorDeleteView(DeleteView):
    """
    Vista para eliminar un proveedor existente.
    """
    model = Proveedor
    template_name = "proveedores_confirm_delete.html"
    success_url = reverse_lazy("products:proveedores")
    pk_url_kwarg = "pk"
    lookup_field = "id_proveedor"

    def get_object(self, queryset=None):
        return self.model.objects.get(id_proveedor=self.kwargs.get(self.pk_url_kwarg))

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Proveedor eliminado correctamente.")
        return super().delete(request, *args, **kwargs)

class MarcasView(TemplateView):
    """
    Vista principal para el CRUD de marcas: muestra la lista y el formulario de alta.
    """
    template_name = "marcas.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["marcas"] = Marca.objects.all()
        context["form"] = MarcaForm()
        return context

    def post(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Manejar petición AJAX
            try:
                form = MarcaForm(request.POST)
                if form.is_valid():
                    marca = form.save()
                    return JsonResponse({
                        'success': True, 
                        'message': 'Marca agregada correctamente.',
                        'data': {
                            'id': marca.id_marca,
                            'marca': marca.marca,
                            'descripcion': marca.descripcion
                        }
                    })
                else:
                    errors = dict(form.errors.items())
                    error_messages = []
                    for field, field_errors in errors.items():
                        for error in field_errors:
                            error_messages.append(f"{field}: {error}")
                    return JsonResponse({
                        'success': False, 
                        'error': '; '.join(error_messages),
                        'errors': errors
                    }, status=400)
            except Exception as e:
                logger.error(f"Error en MarcasView POST AJAX: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'error': f'Error interno del servidor: {str(e)}'
                }, status=500)
        else:
            # Manejar petición normal
            form = MarcaForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Marca agregada correctamente.")
                return redirect("products:marcas")
            context = self.get_context_data(**kwargs)
            context["form"] = form
            return self.render_to_response(context)

class EliminarImagenProductoView(View):
    def post(self, request, pk):
        imagen = get_object_or_404(ProductoImagen, id_imagen=pk)
        producto_id = imagen.producto.id_producto

        # Eliminar el archivo físico
        path = os.path.join(settings.BASE_DIR, 'static', str(imagen.imagen))
        if os.path.isfile(path):
            os.remove(path)

        imagen.delete()

        # Redirige a la lista o edición del producto
        return redirect('products:products_edit_admin', pk=producto_id)


class MarcaUpdateView(UpdateView):
    """
    Vista para editar una marca existente.
    """
    model = Marca
    form_class = MarcaForm
    template_name = "marcas_form.html"
    success_url = reverse_lazy("products:marcas")
    pk_url_kwarg = "pk"
    lookup_field = "id_marca"

    def get_object(self, queryset=None):
        return self.model.objects.get(id_marca=self.kwargs.get(self.pk_url_kwarg))

    def form_valid(self, form):
        messages.success(self.request, "Marca actualizada correctamente.")
        return super().form_valid(form)

class MarcaDeleteView(DeleteView):
    """
    Vista para eliminar una marca existente.
    """
    model = Marca
    template_name = "marcas_confirm_delete.html"
    success_url = reverse_lazy("products:marcas")
    pk_url_kwarg = "pk"
    lookup_field = "id_marca"

    def get_object(self, queryset=None):
        return self.model.objects.get(id_marca=self.kwargs.get(self.pk_url_kwarg))

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Marca eliminada correctamente.")
        return super().delete(request, *args, **kwargs)

class StockView(TemplateView):
    """
    Vista principal para la gestión de stock: muestra la lista de productos con su stock actual.
    """
    template_name = "stock.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener todos los productos con su último registro de stock
        productos_stock = []
        productos = Producto.objects.all()
        
        for producto in productos:
            ultimo_stock = Stock.objects.filter(id_producto=producto).order_by('-fecha_hora').first()
            stock_cantidad = ultimo_stock.cantidad if ultimo_stock else (producto.stock or 0)
            
            productos_stock.append({
                'producto': producto,
                'stock_actual': stock_cantidad,
                'ultimo_movimiento': ultimo_stock.fecha_hora if ultimo_stock else None
            })
        
        context["productos_stock"] = productos_stock
        return context

def actualizar_stock(request):
    """
    Vista para actualizar el stock de un producto específico
    """
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        nueva_cantidad = request.POST.get('cantidad')
        
        try:
            producto = Producto.objects.get(id_producto=producto_id)
            nueva_cantidad = int(nueva_cantidad)
            
            # Actualizar el stock en el producto
            producto.stock = nueva_cantidad
            producto.save()  # Esto automáticamente creará un registro en Stock
            
            messages.success(request, f"Stock actualizado para {producto.nombre}: {nueva_cantidad}")
        except (Producto.DoesNotExist, ValueError):
            messages.error(request, "Error al actualizar el stock")
    
    return redirect('products:stock')

class StockJsonView(View):
    """
    API para obtener datos de stock en formato JSON
    """
    def get(self, request):
        productos_stock = []
        productos = Producto.objects.select_related('id_categoria', 'id_proveedor', 'id_marca').all()
        
        for producto in productos:
            ultimo_stock = Stock.objects.filter(id_producto=producto).order_by('-fecha_hora').first()
            stock_cantidad = ultimo_stock.cantidad if ultimo_stock else (producto.stock or 0)
            
            productos_stock.append({
                'id': producto.id_producto,
                'nombre': producto.nombre,
                'stock_producto': producto.stock or 0,
                'stock_actual': stock_cantidad,
                'categoria': producto.id_categoria.nombre_categoria if producto.id_categoria else '',
                'ultimo_movimiento': ultimo_stock.fecha_hora.strftime('%d/%m/%Y %H:%M') if ultimo_stock else 'Sin movimientos'
            })
        
        return JsonResponse({'data': productos_stock})
    
    

# vistas para el dashboard de administración de productos
    
@method_decorator(permission_required('products', 'ver'), name='dispatch')
class ProductosAdminView(TemplateView):
    template_name = "admin/products/products.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["products"] = Producto.objects.all()
        return context

@method_decorator(permission_required('products', 'crear'), name='dispatch')
class ProductoCreateAdminView(CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = "admin/products/products_form.html"
    success_url = reverse_lazy("products:products_admin")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["productos"] = Producto.objects.all()
        context["imagenes"] = []
        return context

    def form_valid(self, form):
        response = super().form_valid(form)  # Guarda el producto
        producto = self.object  # Ahora sí existe self.object

        for index, imagen in enumerate(self.request.FILES.getlist('imagenes')):
            ruta = procesar_y_guardar_imagen(imagen, producto.id_producto, f"{producto.id_producto}_{index}")
            ProductoImagen.objects.create(producto=producto, imagen=ruta)

        messages.success(self.request, "Producto creado correctamente.")
        return response

@method_decorator(permission_required('products', 'editar'), name='dispatch')
class ProductoUpdateAdminView(UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = "admin/products/products_form.html"
    success_url = reverse_lazy("products:products_admin")
    pk_url_kwarg = "pk"

    def get_object(self, queryset=None):
        return Producto.objects.get(id_producto=self.kwargs.get(self.pk_url_kwarg))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["productos"] = Producto.objects.all()
        context["imagenes"] = ProductoImagen.objects.filter(producto=self.object)
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        producto = self.object

        # Obtener índice más alto de imágenes existentes
        imagenes_existentes = ProductoImagen.objects.filter(producto=producto).values_list('imagen', flat=True)
        indices = []
        for ruta in imagenes_existentes:
            nombre_archivo = os.path.basename(ruta)
            try:
                indice = int(nombre_archivo.split('_')[-1].split('.')[0])
                indices.append(indice)
            except (IndexError, ValueError):
                continue

        siguiente_indice = max(indices) + 1 if indices else 0

        # Guardar nuevas imágenes
        for imagen in self.request.FILES.getlist('imagenes'):
            ruta = procesar_y_guardar_imagen(imagen, producto.id_producto, f"{producto.id_producto}_{siguiente_indice}")
            ProductoImagen.objects.create(producto=producto, imagen=ruta)
            siguiente_indice += 1

        messages.success(self.request, "Producto actualizado correctamente.")
        return response

@method_decorator(permission_required('products', 'eliminar'), name='dispatch')
class ProductoDeleteAdminView(DeleteView):
    model = Producto
    template_name = "admin/products/products_delete.html"
    success_url = reverse_lazy("products:productos")
    pk_url_kwarg = "pk"

    def get_object(self, queryset=None):
        return Producto.objects.get(id_producto=self.kwargs.get(self.pk_url_kwarg))

    def delete(self, request, *args, **kwargs):
        producto = self.get_object()
        imagenes = ProductoImagen.objects.filter(producto=producto)
        for imagen in imagenes:
            path = os.path.join(settings.BASE_DIR, 'static', imagen.imagen)
            if os.path.exists(path):
                os.remove(path)
        imagenes.delete()
        producto.delete()
        messages.success(request, "Producto eliminado correctamente.")
        return redirect(self.success_url)

@method_decorator(permission_required('products', 'editar'), name='dispatch')
class EliminarImagenProductoAdminView(View):
    def post(self, request, pk):
        imagen = get_object_or_404(ProductoImagen, id_imagen=pk)
        producto_id = imagen.producto.id_producto

        # Eliminar el archivo físico
        path = os.path.join(settings.BASE_DIR, 'static', str(imagen.imagen))
        if os.path.isfile(path):
            os.remove(path)

        imagen.delete()

        # Redirige a la lista o edición del producto
        return redirect('products:products_edit_admin', pk=producto_id)
    
# desde este comendario hacia abajo es el codigo que se utlisa en el dashboard, estas son las vistas que se tienen que proteger las otras seran desactivadas 
# vistas para el dashboard de administración de cateegorías

@method_decorator(permission_required('brands', 'ver'), name='dispatch')
class BrandsAdminView(TemplateView):
    template_name = "admin/brands/brands.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["brands"] = Marca.objects.all()
        return context

@method_decorator(permission_required('brands', 'crear'), name='dispatch')
class BrandCreateAdminView(CreateView):
    model = Marca
    form_class = MarcaForm
    template_name = "admin/brands/brands_form.html"
    success_url = reverse_lazy("products:brands_admin")

    def form_valid(self, form):
        messages.success(self.request, "Brand created successfully.")
        return super().form_valid(form)

@method_decorator(permission_required('brands', 'editar'), name='dispatch')
class BrandUpdateAdminView(UpdateView):
    model = Marca
    form_class = MarcaForm
    template_name = "admin/brands/brands_form.html"
    success_url = reverse_lazy("products:brands_admin")
    pk_url_kwarg = "pk"

    def get_object(self, queryset=None):
        return Marca.objects.get(id_marca=self.kwargs.get(self.pk_url_kwarg))

    def form_valid(self, form):
        messages.success(self.request, "Brand updated successfully.")
        return super().form_valid(form)

@method_decorator(permission_required('brands', 'eliminar'), name='dispatch')
class BrandDeleteAdminView(DeleteView):
    model = Marca
    template_name = "admin/brands/brands_delete.html"
    success_url = reverse_lazy("products:brands_admin")
    pk_url_kwarg = "pk"

    def get_object(self, queryset=None):
        return Marca.objects.get(id_marca=self.kwargs.get(self.pk_url_kwarg))

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Brand deleted successfully.")
        return super().delete(request, *args, **kwargs)

@method_decorator(permission_required('providers', 'ver'), name='dispatch')
class ProveedoresAdminView(TemplateView):
    template_name = "admin/proveedores/proveedores.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["proveedores"] = Proveedor.objects.all()
        return context

@method_decorator(permission_required('providers', 'crear'), name='dispatch')
class ProveedorCreateAdminView(CreateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = "admin/proveedores/proveedores_form.html"
    success_url = reverse_lazy("products:proveedores_admin")

    def form_valid(self, form):
        messages.success(self.request, "Proveedor creado correctamente.")
        return super().form_valid(form)

@method_decorator(permission_required('providers', 'editar'), name='dispatch')
class ProveedorUpdateAdminView(UpdateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = "admin/proveedores/proveedores_form.html"
    success_url = reverse_lazy("products:proveedores_admin")
    pk_url_kwarg = "pk"

    def get_object(self, queryset=None):
        return Proveedor.objects.get(id_proveedor=self.kwargs.get(self.pk_url_kwarg))

    def form_valid(self, form):
        messages.success(self.request, "Proveedor actualizado correctamente.")
        return super().form_valid(form)

@method_decorator(permission_required('providers', 'eliminar'), name='dispatch')
class ProveedorDeleteAdminView(DeleteView):
    model = Proveedor
    template_name = "admin/proveedores/proveedores_delete.html"
    success_url = reverse_lazy("products:proveedores_admin")
    pk_url_kwarg = "pk"

    def get_object(self, queryset=None):
        return Proveedor.objects.get(id_proveedor=self.kwargs.get(self.pk_url_kwarg))

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Proveedor eliminado correctamente.")
        return super().delete(request, *args, **kwargs)
    
@method_decorator(permission_required('categories', 'ver'), name='dispatch')
class CategoriasAdminView(TemplateView):
    template_name = "admin/categories/categories.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categorias"] = Categoria.objects.all()
        return context

@method_decorator(permission_required('categories', 'crear'), name='dispatch')
class CategoriaCreateAdminView(CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = "admin/categories/categories_form.html"
    success_url = reverse_lazy("products:categories_admin")

    def form_valid(self, form):
        messages.success(self.request, "Categoría creada correctamente.")
        return super().form_valid(form)

@method_decorator(permission_required('categories', 'editar'), name='dispatch')
class CategoriaUpdateAdminView(UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = "admin/categories/categories_form.html"
    success_url = reverse_lazy("products:categories_admin")
    pk_url_kwarg = "pk"

    def get_object(self, queryset=None):
        return Categoria.objects.get(id_categoria=self.kwargs.get(self.pk_url_kwarg))

    def form_valid(self, form):
        messages.success(self.request, "Categoría actualizada correctamente.")
        return super().form_valid(form)

@method_decorator(permission_required('categories', 'eliminar'), name='dispatch')
class CategoriaDeleteAdminView(DeleteView):
    model = Categoria
    template_name = "admin/categories/categories_delete.html"
    success_url = reverse_lazy("products:categories_admin")
    pk_url_kwarg = "pk"

    def get_object(self, queryset=None):
        return Categoria.objects.get(id_categoria=self.kwargs.get(self.pk_url_kwarg))

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Categoría eliminada correctamente.")
        return super().delete(request, *args, **kwargs)

