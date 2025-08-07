from django.shortcuts import render
from django.views.generic import TemplateView
from products.models import Producto, Categoria
from tables.models import Mesa 
from roles.decorators import permission_required
from django.utils.decorators import method_decorator
from notifications.utils import notificar_usuario


@method_decorator(permission_required('dashboard', 'ver'), name='dispatch')
class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['productos'] = Producto.objects.count()
        context['categorias'] = Categoria.objects.count()
        context['mesas'] = Mesa.objects.count()
        # Enviar notificación al usuario actual
        if self.request.user.is_authenticated:
            mensaje = f"¡Bienvenido al dashboard, {self.request.user.first_name or self.request.user.username}!"
            notificar_usuario(self.request.user, mensaje)
        return context