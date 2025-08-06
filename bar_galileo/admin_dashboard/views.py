from django.shortcuts import render

from django.views.generic import TemplateView
from products.models import Producto, Categoria
from tables.models import Mesa 
from roles.decorators import permission_required
from django.utils.decorators import method_decorator


@method_decorator(permission_required('dashboard', 'ver'), name='dispatch')
class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['productos'] = Producto.objects.count()
        context['categorias'] = Categoria.objects.count()
        context['mesas'] = Mesa.objects.count()
        return context