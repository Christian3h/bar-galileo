from django.shortcuts import render
from django.views.generic import TemplateView
from products.models import Producto, Categoria
from tables.models import Mesa, Pedido, PedidoItem, Factura
from expenses.models import Expense
from nominas.models import Empleado, Pago, Bonificacion
from roles.decorators import permission_required
from django.utils.decorators import method_decorator
from notifications.utils import notificar_usuario
from django.db.models import Sum, Count, F, ExpressionWrapper, DecimalField
from django.db.models.functions import TruncDay
from datetime import datetime, timedelta

def get_date_range(period):
    today = datetime.now().date()
    if period == 'month':
        start_date = today.replace(day=1)
        # Go to the next month and subtract one day to get the end of the current month
        next_month = (start_date.replace(day=28) + timedelta(days=4)).replace(day=1)
        end_date = next_month - timedelta(days=1)
    elif period == 'quarter':
        current_quarter = (today.month - 1) // 3 + 1
        start_month = 3 * current_quarter - 2
        start_date = today.replace(month=start_month, day=1)
        end_month = 3 * current_quarter
        # handle end of year
        if end_month == 12:
            end_date = today.replace(year=today.year, month=12, day=31)
        else:
            end_date = (today.replace(month=end_month + 1, day=1)) - timedelta(days=1)
    else: # all
        start_date = None
        end_date = None
    return start_date, end_date

@method_decorator(permission_required('dashboard', 'ver'), name='dispatch')
class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        period = self.request.GET.get('period', 'month') # Default to month
        start_date, end_date = get_date_range(period)

        # Filtered querysets
        facturas_periodo = Factura.objects.all()
        pedidos_periodo = PedidoItem.objects.filter(pedido__factura__isnull=False)
        gastos_periodo = Expense.objects.all()
        pagos_periodo = Pago.objects.all()

        if start_date and end_date:
            facturas_periodo = facturas_periodo.filter(fecha__date__range=[start_date, end_date])
            pedidos_periodo = pedidos_periodo.filter(pedido__factura__fecha__date__range=[start_date, end_date])
            gastos_periodo = gastos_periodo.filter(date__range=[start_date, end_date])
            pagos_periodo = pagos_periodo.filter(fecha_pago__range=[start_date, end_date])

        context['productos'] = Producto.objects.count()
        context['categorias'] = Categoria.objects.count()
        context['mesas'] = Mesa.objects.count()

        # Data for charts
        context['total_mesas_disponibles'] = Mesa.objects.filter(estado='disponible').count()
        context['total_mesas_ocupadas'] = Mesa.objects.filter(estado='ocupada').count()
        context['total_mesas_reservadas'] = Mesa.objects.filter(estado='reservada').count()
        context['total_mesas_fuera_de_servicio'] = Mesa.objects.filter(estado='fuera de servicio').count()

        context['top_5_productos_mas_vendidos'] = pedidos_periodo.values('producto__nombre').annotate(total_vendido=Sum('cantidad')).order_by('-total_vendido')[:5]

        # New data
        context['ingresos_totales'] = facturas_periodo.aggregate(total=Sum('total'))['total'] or 0
        context['productos_mas_stock'] = Producto.objects.order_by('-stock')[:5]
        context['valor_total_stock'] = Producto.objects.aggregate(total=Sum(F('stock') * F('precio_compra')))['total'] or 0

        # Monthly sales (or period sales)
        ventas_periodo = facturas_periodo.annotate(dia=TruncDay('fecha')).values('dia').annotate(total_dia=Sum('total')).order_by('dia')
        context['ventas_periodo'] = list(ventas_periodo) # Convert to list to be able to serialize it

        # Total profit
        ganancia_total = pedidos_periodo.annotate(
            ganancia_item=ExpressionWrapper(
                (F('precio_unitario') - F('producto__precio_compra')) * F('cantidad'),
                output_field=DecimalField()
            )
        ).aggregate(total=Sum('ganancia_item'))['total'] or 0
        context['ganancia_total'] = ganancia_total

        context['gastos_totales'] = gastos_periodo.aggregate(total=Sum('amount'))['total'] or 0
        
        # Nóminas data
        context['total_empleados'] = Empleado.objects.filter(estado='activo').count()
        context['total_empleados_inactivos'] = Empleado.objects.filter(estado='inactivo').count()
        context['nominas_pagadas'] = pagos_periodo.aggregate(total=Sum('monto'))['total'] or 0
        context['bonificaciones_activas'] = Bonificacion.objects.filter(activa=True).count()
        
        # Total de bonificaciones pagadas como pagos de tipo "bono" en el periodo
        bonificaciones_periodo = pagos_periodo.filter(tipo='bono').aggregate(total_bonificaciones=Sum('monto'))['total_bonificaciones'] or 0
        context['bonificaciones_pagadas'] = bonificaciones_periodo
        
        # Pagos por empleado (top 5 con mayores pagos en el periodo)
        top_pagos = pagos_periodo.values('empleado__nombre').annotate(
            total_pagado=Sum('monto')
        ).order_by('-total_pagado')[:5]
        context['top_pagos_empleados'] = top_pagos
        
        context['selected_period'] = period

        # Enviar notificación al usuario actual
        if self.request.user.is_authenticated:
            mensaje = f"¡Bienvenido al dashboard, {self.request.user.first_name or self.request.user.username}!"
            notificar_usuario(self.request.user, mensaje)
        return context
