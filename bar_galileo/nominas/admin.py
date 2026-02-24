from django.contrib import admin
from .models import Empleado, Pago, Bonificacion

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'cargo', 'salario', 'estado', 'user', 'fecha_contratacion']
    list_filter = ['estado', 'tipo_contrato', 'cargo']
    search_fields = ['nombre', 'cargo', 'email']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']

    fieldsets = (
        ('Información Personal', {
            'fields': ('user', 'nombre', 'cargo', 'email', 'telefono', 'direccion')
        }),
        ('Información Laboral', {
            'fields': ('salario', 'fecha_contratacion', 'estado', 'tipo_contrato')
        }),
        ('Metadata', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ['empleado', 'fecha_pago', 'monto', 'tipo', 'created_by', 'fecha_creacion']
    list_filter = ['tipo', 'fecha_pago']
    search_fields = ['empleado__nombre', 'descripcion']
    date_hierarchy = 'fecha_pago'
    readonly_fields = ['created_by', 'modified_by', 'fecha_creacion', 'fecha_modificacion']

    def save_model(self, request, obj, form, change):
        if not change:  # Si es un objeto nuevo
            obj.created_by = request.user
        obj.modified_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Bonificacion)
class BonificacionAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'empleado', 'monto', 'recurrente', 'activa', 'fecha_inicio', 'fecha_fin', 'created_by']
    list_filter = ['recurrente', 'activa', 'fecha_inicio']
    search_fields = ['nombre', 'empleado__nombre']
    readonly_fields = ['created_by', 'modified_by', 'fecha_creacion', 'fecha_modificacion']

    def save_model(self, request, obj, form, change):
        if not change:  # Si es un objeto nuevo
            obj.created_by = request.user
        obj.modified_by = request.user
        super().save_model(request, obj, form, change)
