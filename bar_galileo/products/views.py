# Vistas públicas y de autenticación para la aplicación Bar Galileo
#
# Este archivo contiene las vistas principales del sistema, incluyendo:
# - Vistas públicas (inicio, nosotros, menú, reservas)
# - Autenticación de usuarios (login, logout, registro)
# - CRUD de productos (listar, agregar, editar, eliminar)
#
# Cada clase y método está documentado para facilitar el mantenimiento y la extensión del sistema.

from django.views.generic import TemplateView, View
from django.views.generic.edit import FormView
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.contrib import messages
from .models import Categoria, Producto, Proveedor, Marca
from .forms import ProductoForm, CategoriaForm, ProveedorForm, MarcaForm
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.views.generic import UpdateView, DeleteView


# Vistas públicas
class IndexView(TemplateView):
    """
    Vista de la página principal.
    """
    template_name = "public/index.html"

class NosotrosView(TemplateView):
    """
    Vista de la página 'Nosotros'.
    """
    template_name = "public/nosotros.html"

class MenuView(TemplateView):
    """
    Vista del menú de productos, muestra categorías y productos.
    """
    template_name = "public/menu.html"

    def get_context_data(self, **kwargs):
        """
        Agrega categorías y productos al contexto para el template del menú.
        """
        context = super().get_context_data(**kwargs)
        context["categorias"] = Categoria.objects.all()
        context["productos"] = Producto.objects.select_related("id_categoria")
        return context

# Reservas
class ReservaEventosView(TemplateView):
    """
    Vista para reservas de eventos.
    """
    template_name = "public/reservas/eventos.html"

class ReservaGrupalView(TemplateView):
    """
    Vista para reservas grupales.
    """
    template_name = "public/reservas/grupal.html"

# Autenticación básica
class LoginView(View):
    """
    Vista para inicio de sesión de usuario.
    """
    def get(self, request):
        """Muestra el formulario de login."""
        return render(request, "auth/login.html")

    def post(self, request):
        """Procesa el login del usuario."""
        user = authenticate(request, username=request.POST["username"], password=request.POST["password"])
        if user is not None:
            login(request, user)
            return redirect("index")
        messages.error(request, "Usuario o contraseña incorrectos")
        return render(request, "auth/login.html")

class LogoutView(View):
    """
    Vista para cerrar sesión de usuario.
    """
    def get(self, request):
        """Cierra la sesión y redirige al inicio."""
        logout(request)
        return redirect("index")

class SignupView(View):
    """
    Vista para registro de nuevos usuarios.
    """
    def get(self, request):
        """Muestra el formulario de registro."""
        return render(request, "auth/signup.html")

    def post(self, request):
        """Procesa el registro de usuario."""
        username = request.POST["username"]
        password = request.POST["password"]
        if User.objects.filter(username=username).exists():
            messages.error(request, "El usuario ya existe")
        else:
            User.objects.create_user(username=username, password=password)
            messages.success(request, "Cuenta creada. Inicia sesión.")
            return redirect("login")
        return render(request, "auth/signup.html")

class ProductosJsonView(View):
    """
    API para obtener los productos en formato JSON (usado por DataTables).
    """
    def get(self, request):
        """Devuelve la lista de productos en formato JSON."""
        productos = Producto.objects.select_related('id_categoria', 'id_proveedor', 'id_marca').all()
        data = []
        for producto in productos:
            imagen_url = producto.imagen.url if producto.imagen else ''
            data.append({
                'id': producto.id_producto,
                'nombre': producto.nombre,
                'precio': str(producto.precio),
                'precio_compra': str(producto.precio_compra) if producto.precio_compra is not None else '',
                'precio_venta': str(producto.precio_venta) if producto.precio_venta is not None else '',
                'stock': producto.stock if producto.stock is not None else '',
                'descripcion': producto.descripcion or '',
                'categoria': producto.id_categoria.nombre_categoria if producto.id_categoria else '',
                'proveedor': producto.id_proveedor.nombre if producto.id_proveedor else '',
                'marca': producto.id_marca.marca if producto.id_marca else '',
                'imagen_url': request.build_absolute_uri(imagen_url) if imagen_url else '',
            })
        return JsonResponse({'data': data})

class ProductosView(TemplateView):
    """
    Vista principal para el CRUD de productos: muestra la lista y el formulario de alta.
    """
    template_name = "productos.html"

    def get_context_data(self, **kwargs):
        """
        Agrega la lista de productos y el formulario al contexto.
        """
        context = super().get_context_data(**kwargs)
        context["productos"] = Producto.objects.all()
        context["form"] = ProductoForm()
        return context

    def post(self, request, *args, **kwargs):
        """
        Procesa el alta de un nuevo producto.
        """
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto agregado correctamente.")
            return redirect("productos")
        context = self.get_context_data(**kwargs)
        context["form"] = form
        return self.render_to_response(context)

class ProductoUpdateView(UpdateView):
    """
    Vista para editar un producto existente.
    """
    model = Producto
    form_class = ProductoForm
    template_name = "productos_form.html"
    success_url = reverse_lazy("productos")
    pk_url_kwarg = "pk"
    lookup_field = "id_producto"

    def get_object(self, queryset=None):
        return self.model.objects.get(id_producto=self.kwargs.get(self.pk_url_kwarg))

    def form_valid(self, form):
        """Muestra mensaje de éxito al actualizar."""
        messages.success(self.request, "Producto actualizado correctamente.")
        return super().form_valid(form)

class ProductoDeleteView(DeleteView):
    """
    Vista para eliminar un producto existente.
    """
    model = Producto
    template_name = "productos_confirm_delete.html"
    success_url = reverse_lazy("productos")
    pk_url_kwarg = "pk"
    lookup_field = "id_producto"

    def get_object(self, queryset=None):
        return self.model.objects.get(id_producto=self.kwargs.get(self.pk_url_kwarg))

    def delete(self, request, *args, **kwargs):
        """Muestra mensaje de éxito al eliminar."""
        messages.success(self.request, "Producto eliminado correctamente.")
        return super().delete(request, *args, **kwargs)

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