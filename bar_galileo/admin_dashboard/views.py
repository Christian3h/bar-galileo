from django.shortcuts import render
from django.views.generic import TemplateView
from products.models import Producto, Categoria
from tables.models import Mesa, Pedido, PedidoItem, Factura
from roles.decorators import permission_required
from django.utils.decorators import method_decorator
from notifications.utils import notificar_usuario
from django.db.models import Sum, Count, F, ExpressionWrapper, DecimalField
from django.db.models.functions import TruncDay
from datetime import datetime

@method_decorator(permission_required('dashboard', 'ver'), name='dispatch')
class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['productos'] = Producto.objects.count()
        context['categorias'] = Categoria.objects.count()
        context['mesas'] = Mesa.objects.count()

        # Data for charts
        context['total_mesas_disponibles'] = Mesa.objects.filter(estado='disponible').count()
        context['total_mesas_ocupadas'] = Mesa.objects.filter(estado='ocupada').count()
        context['total_mesas_reservadas'] = Mesa.objects.filter(estado='reservada').count()
        context['total_mesas_fuera_de_servicio'] = Mesa.objects.filter(estado='fuera de servicio').count()

        context['top_5_productos_mas_vendidos'] = PedidoItem.objects.values('producto__nombre').annotate(total_vendido=Sum('cantidad')).order_by('-total_vendido')[:5]

        # New data
        context['ingresos_totales'] = Factura.objects.aggregate(total=Sum('total'))['total'] or 0
        context['productos_mas_stock'] = Producto.objects.order_by('-stock')[:5]
        context['valor_total_stock'] = Producto.objects.aggregate(total=Sum(F('stock') * F('precio_compra')))['total'] or 0

        # Monthly sales
        today = datetime.now()
        ventas_mensuales = Factura.objects.filter(fecha__year=today.year, fecha__month=today.month).annotate(dia=TruncDay('fecha')).values('dia').annotate(total_dia=Sum('total')).order_by('dia')
        context['ventas_mensuales'] = ventas_mensuales

        # Total profit
        ganancia_total = PedidoItem.objects.filter(pedido__factura__isnull=False).annotate(
            ganancia_item=ExpressionWrapper(
                (F('precio_unitario') - F('producto__precio_compra')) * F('cantidad'),
                output_field=DecimalField()
            )
        ).aggregate(total=Sum('ganancia_item'))['total'] or 0
        context['ganancia_total'] = ganancia_total

        # Enviar notificación al usuario actual
        if self.request.user.is_authenticated:
            mensaje = f"¡Bienvenido al dashboard, {self.request.user.first_name or self.request.user.username}!"
            notificar_usuario(self.request.user, mensaje)
        return context