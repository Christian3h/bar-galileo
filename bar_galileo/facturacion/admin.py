from django.contrib import admin
from tables.models import Factura

@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ['numero', 'pedido', 'fecha', 'total']
    list_filter = ['fecha']
    search_fields = ['numero', 'pedido__mesa__nombre']
    readonly_fields = ['numero', 'total']
    ordering = ['-fecha']
