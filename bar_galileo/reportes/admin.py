from django.contrib import admin
from .models import Reporte


@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo', 'creado_por', 'fecha_inicio', 'fecha_fin', 'fecha_creacion']
    list_filter = ['tipo', 'fecha_creacion', 'creado_por']
    search_fields = ['nombre', 'descripcion']
    date_hierarchy = 'fecha_creacion'
    readonly_fields = ['fecha_creacion', 'creado_por']
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)
