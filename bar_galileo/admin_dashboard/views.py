from django.shortcuts import render
from django.views.generic import TemplateView
from products.models import Producto, Categoria
from tables.models import Mesa, Pedido, PedidoItem, Factura
from expenses.models import Expense
from roles.decorators import permission_required
from django.utils.decorators import method_decorator
from notifications.utils import notificar_usuario
from django.db.models import Sum, Count, F, ExpressionWrapper, DecimalField
from django.db.models.functions import TruncDay
from datetime import datetime, timedelta
from django.http import HttpResponse
import csv
from io import BytesIO
from django.template.loader import render_to_string

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

        if start_date and end_date:
            facturas_periodo = facturas_periodo.filter(fecha__date__range=[start_date, end_date])
            pedidos_periodo = pedidos_periodo.filter(pedido__factura__fecha__date__range=[start_date, end_date])
            gastos_periodo = gastos_periodo.filter(date__range=[start_date, end_date])

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
        
        context['selected_period'] = period

        # Enviar notificación al usuario actual
        if self.request.user.is_authenticated:
            mensaje = f"¡Bienvenido al dashboard, {self.request.user.first_name or self.request.user.username}!"
            notificar_usuario(self.request.user, mensaje)
        return context


def _build_dashboard_context(request):
    """Helper para construir el mismo contexto que DashboardView (usado por export)."""
    period = request.GET.get('period', 'month')
    start_date, end_date = get_date_range(period)

    facturas_periodo = Factura.objects.all()
    pedidos_periodo = PedidoItem.objects.filter(pedido__factura__isnull=False)
    gastos_periodo = Expense.objects.all()

    if start_date and end_date:
        facturas_periodo = facturas_periodo.filter(fecha__date__range=[start_date, end_date])
        pedidos_periodo = pedidos_periodo.filter(pedido__factura__fecha__date__range=[start_date, end_date])
        gastos_periodo = gastos_periodo.filter(date__range=[start_date, end_date])

    ingresos_totales = facturas_periodo.aggregate(total=Sum('total'))['total'] or 0
    ventas_periodo = facturas_periodo.annotate(dia=TruncDay('fecha')).values('dia').annotate(total_dia=Sum('total')).order_by('dia')
    ganancia_total = pedidos_periodo.annotate(
        ganancia_item=ExpressionWrapper(
            (F('precio_unitario') - F('producto__precio_compra')) * F('cantidad'),
            output_field=DecimalField()
        )
    ).aggregate(total=Sum('ganancia_item'))['total'] or 0
    valor_total_stock = Producto.objects.aggregate(total=Sum(F('stock') * F('precio_compra')))['total'] or 0
    gastos_totales = gastos_periodo.aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'period': period,
        'ingresos_totales': ingresos_totales,
        'ventas_periodo': list(ventas_periodo),
        'ganancia_total': ganancia_total,
        'valor_total_stock': valor_total_stock,
        'gastos_totales': gastos_totales,
    }
    return context


def export_dashboard(request, fmt):
    """Exportar estadísticas generales en CSV o PDF (fallback HTML si no hay reportlab).
    fmt: 'csv' o 'pdf'
    """
    try:
        ctx = _build_dashboard_context(request)
    except Exception as e:
        return HttpResponse(f"Error generando reporte: {e}", status=500)

    if fmt == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="estadisticas_generales.csv"'
        writer = csv.writer(response)

        # Escribir métricas principales
        writer.writerow(['Métrica', 'Valor'])
        writer.writerow(['Ingresos Totales', ctx['ingresos_totales']])
        writer.writerow(['Ganancia Total', ctx['ganancia_total']])
        writer.writerow(['Valor Total del Stock', ctx['valor_total_stock']])
        writer.writerow(['Gastos Totales', ctx['gastos_totales']])
        writer.writerow([])
        writer.writerow(['Ventas por Día'])
        writer.writerow(['Fecha', 'Total'])
        for v in ctx['ventas_periodo']:
            fecha = v.get('dia')
            total = v.get('total_dia')
            writer.writerow([fecha, total])

        return response

    elif fmt == 'pdf':
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
        except Exception:
            html = render_to_string('admin_dashboard/report_pdf.html', {
                'estadisticas': ctx
            })
            return HttpResponse(html, content_type='text/html')

        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        x = 40
        y = height - 40

        p.setFont('Helvetica-Bold', 16)
        p.drawString(x, y, 'Estadísticas Generales')
        y -= 30

        p.setFont('Helvetica', 12)
        p.drawString(x, y, f"Ingresos Totales: {ctx['ingresos_totales']}")
        y -= 18
        p.drawString(x, y, f"Ganancia Total: {ctx['ganancia_total']}")
        y -= 18
        p.drawString(x, y, f"Valor Total del Stock: {ctx['valor_total_stock']}")
        y -= 18
        p.drawString(x, y, f"Gastos Totales: {ctx['gastos_totales']}")
        y -= 24

        p.drawString(x, y, 'Ventas por Día:')
        y -= 18
        for v in ctx['ventas_periodo']:
            if y < 60:
                p.showPage()
                y = height - 40
            fecha = v.get('dia')
            total = v.get('total_dia')
            p.drawString(x, y, f"{fecha}: {total}")
            y -= 14

        p.showPage()
        p.save()
        pdf = buffer.getvalue()
        buffer.close()
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="estadisticas_generales.pdf"'
        response.write(pdf)
        return response

    else:
        return HttpResponse('Formato no soportado', status=400)
