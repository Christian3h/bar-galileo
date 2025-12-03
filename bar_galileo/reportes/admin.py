from django.contrib import admin
from .models import Reporte


@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'periodo', 'formato', 'creado_por', 'fecha_creacion', 'generado')
    list_filter = ('tipo', 'periodo', 'formato', 'generado', 'fecha_creacion')
    search_fields = ('nombre', 'descripcion', 'creado_por__username')
    readonly_fields = ('fecha_creacion', 'archivo')
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'tipo', 'descripcion')
        }),
        ('Configuración', {
            'fields': ('periodo', 'formato', 'fecha_inicio', 'fecha_fin')
        }),
        ('Estado', {
            'fields': ('generado', 'archivo', 'creado_por', 'fecha_creacion')
        })
    )
