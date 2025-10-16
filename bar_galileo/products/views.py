# Vistas públicas y de autenticación para la aplicación Bar Galileo
#
# Este archivo contiene las vistas principales del sistema, incluyendo:
# - Vistas públicas (inicio, nosotros, menú, reservas)
# - Autenticación de usuarios (login, logout, registro)
# - CRUD de productos (listar, agregar, editar, eliminar)
#
# Cada clase y método está documentado para facilitar el mantenimiento y la extensión del sistema.

from django.views.generic import TemplateView, View, UpdateView, DeleteView, CreateView, DetailView
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from .models import Categoria, Producto, Proveedor, Marca, ProductoImagen, procesar_y_guardar_imagen, Stock
from .forms import ProductoForm, CategoriaForm, ProveedorForm, MarcaForm
import os
import logging
from django.utils.decorators import method_decorator
from roles.decorators import permission_required
from notifications.utils import notificar_usuario


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
        response = super().form_valid(form)
        producto = self.object

        for index, imagen in enumerate(self.request.FILES.getlist('imagenes')):
            ruta = procesar_y_guardar_imagen(imagen, producto.id_producto, f"{producto.id_producto}_{index}")
            ProductoImagen.objects.create(producto=producto, imagen=ruta)

        mensaje = f"Se ha creado el nuevo producto: '{producto.nombre}'."
        notificar_usuario(self.request.user, mensaje)
        return response



        return response

@method_decorator(permission_required('products', 'eliminar'), name='dispatch')
class ProductoDeleteAdminView(DeleteView):
    model = Producto
    template_name = "admin/products/products_delete.html"
    success_url = reverse_lazy("products:products_admin")
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
        mensaje = f"El producto '{producto.nombre}' ha sido eliminado."
        notificar_usuario(request.user, mensaje)
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

# desde este comendario hacia abajo es el codigo que se utliza en el dashboard, estas son las vistas que se tienen que proteger las otras seran desactivadas
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
        response = super().form_valid(form)
        mensaje = f"La marca '{self.object.marca}' ha sido creada."
        notificar_usuario(self.request.user, mensaje)
        return response

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
        response = super().form_valid(form)
        mensaje = f"La marca '{self.object.marca}' ha sido actualizada."
        notificar_usuario(self.request.user, mensaje)
        return response

@method_decorator(permission_required('brands', 'eliminar'), name='dispatch')
class BrandDeleteAdminView(DeleteView):
    model = Marca
    template_name = "admin/brands/brands_delete.html"
    success_url = reverse_lazy("products:brands_admin")
    pk_url_kwarg = "pk"

    def get_object(self, queryset=None):
        return Marca.objects.get(id_marca=self.kwargs.get(self.pk_url_kwarg))

    def delete(self, request, *args, **kwargs):
        brand = self.get_object()
        mensaje = f"La marca '{brand.marca}' ha sido eliminada."
        response = super().delete(request, *args, **kwargs)
        notificar_usuario(request.user, mensaje)
        return response

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
        response = super().form_valid(form)
        mensaje = f"El proveedor '{self.object.nombre}' ha sido creado."
        notificar_usuario(self.request.user, mensaje)
        return response

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
        response = super().form_valid(form)
        mensaje = f"El proveedor '{self.object.nombre}' ha sido actualizado."
        notificar_usuario(self.request.user, mensaje)
        return response

@method_decorator(permission_required('providers', 'eliminar'), name='dispatch')
class ProveedorDeleteAdminView(DeleteView):
    model = Proveedor
    template_name = "admin/proveedores/proveedores_delete.html"
    success_url = reverse_lazy("products:proveedores_admin")
    pk_url_kwarg = "pk"

    def get_object(self, queryset=None):
        return Proveedor.objects.get(id_proveedor=self.kwargs.get(self.pk_url_kwarg))

    def delete(self, request, *args, **kwargs):
        proveedor = self.get_object()
        mensaje = f"El proveedor '{proveedor.nombre}' ha sido eliminado."
        response = super().delete(request, *args, **kwargs)
        notificar_usuario(request.user, mensaje)
        return response

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
        response = super().form_valid(form)
        mensaje = f"La categoría '{self.object.nombre_categoria}' ha sido creada."
        notificar_usuario(self.request.user, mensaje)
        return response

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
        response = super().form_valid(form)
        mensaje = f"La categoría '{self.object.nombre_categoria}' ha sido actualizada."
        notificar_usuario(self.request.user, mensaje)
        return response

@method_decorator(permission_required('categories', 'eliminar'), name='dispatch')
class CategoriaDeleteAdminView(DeleteView):
    model = Categoria
    template_name = "admin/categories/categories_delete.html"
    success_url = reverse_lazy("products:categories_admin")
    pk_url_kwarg = "pk"

    def get_object(self, queryset=None):
        return Categoria.objects.get(id_categoria=self.kwargs.get(self.pk_url_kwarg))

    def delete(self, request, *args, **kwargs):
        categoria = self.get_object()
        mensaje = f"La categoría '{categoria.nombre_categoria}' ha sido eliminada."
        response = super().delete(request, *args, **kwargs)
        notificar_usuario(request.user, mensaje)
        return response

class ProductoDetailView(DetailView):
    model = Producto
    template_name = "products/producto_detalle.html"
    context_object_name = "producto"

    def get_object(self, queryset=None):
        return get_object_or_404(Producto, id_producto=self.kwargs.get("pk"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        producto_actual = self.object
        
        # Obtener productos relacionados (misma marca, excluyendo el producto actual)
        productos_relacionados = Producto.objects.filter(
            id_marca=producto_actual.id_marca
        ).exclude(
            id_producto=producto_actual.id_producto
        )[:4] # Limitar a 4 productos relacionados
        
        context['productos_relacionados'] = productos_relacionados
        return context

