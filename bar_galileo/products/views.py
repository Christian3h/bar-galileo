# Vistas públicas y de autenticación para la aplicación Bar Galileo
#
# Este archivo contiene las vistas principales del sistema, incluyendo:
# - Vistas públicas (inicio, nosotros, menú, reservas)
# - Autenticación de usuarios (login, logout, registro)
# - CRUD de productos (listar, agregar, editar, eliminar)
#
# Cada clase y método está documentado para facilitar el mantenimiento y la extensión del sistema.

from django.views.generic import TemplateView, View, UpdateView, DeleteView
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from .models import Categoria, Producto, Proveedor, Marca, ProductoImagen, procesar_y_guardar_imagen
from .forms import ProductoForm, CategoriaForm, ProveedorForm, MarcaForm
import os

class ProductosJsonView(View):
    def get(self, request):
        productos = Producto.objects.select_related('id_categoria', 'id_proveedor', 'id_marca').prefetch_related('imagenes').all()
        data = []
        for producto in productos:
            primera_imagen = producto.imagenes.first()
            imagen_url = request.build_absolute_uri(f'/static/{primera_imagen.imagen}') if primera_imagen else ''
            data.append({
                'id': producto.id_producto,
                'nombre': producto.nombre,
                'precio': str(producto.precio),
                'precio_compra': str(producto.precio_compra or ''),
                'precio_venta': str(producto.precio_venta or ''),
                'stock': producto.stock or '',
                'descripcion': producto.descripcion or '',
                'categoria': producto.id_categoria.nombre_categoria if producto.id_categoria else '',
                'proveedor': producto.id_proveedor.nombre if producto.id_proveedor else '',
                'marca': producto.id_marca.marca if producto.id_marca else '',
                'imagen_url': imagen_url,
            })
        return JsonResponse({'data': data})

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
        return redirect('productos')
    
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
            return redirect("productos")
        context = self.get_context_data()
        context["form"] = form
        return self.render_to_response(context)


class ProductoUpdateView(UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = "productos_form.html"
    success_url = reverse_lazy("productos")
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
    success_url = reverse_lazy("productos")
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
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoría agregada correctamente.")
            return redirect("categorias")
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
    success_url = reverse_lazy("categorias")
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
    success_url = reverse_lazy("categorias")
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
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Proveedor agregado correctamente.")
            return redirect("proveedores")
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
    success_url = reverse_lazy("proveedores")
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
    success_url = reverse_lazy("proveedores")
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
        form = MarcaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Marca agregada correctamente.")
            return redirect("marcas")
        context = self.get_context_data(**kwargs)
        context["form"] = form
        return self.render_to_response(context)

class MarcaUpdateView(UpdateView):
    """
    Vista para editar una marca existente.
    """
    model = Marca
    form_class = MarcaForm
    template_name = "marcas_form.html"
    success_url = reverse_lazy("marcas")
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
    success_url = reverse_lazy("marcas")
    pk_url_kwarg = "pk"
    lookup_field = "id_marca"

    def get_object(self, queryset=None):
        return self.model.objects.get(id_marca=self.kwargs.get(self.pk_url_kwarg))

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Marca eliminada correctamente.")
        return super().delete(request, *args, **kwargs)