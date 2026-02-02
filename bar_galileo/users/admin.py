from django.contrib import admin
from .models import PerfilUsuario, Emergencia, CambioPasswordAuditoria


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ['user', 'nombre', 'cedula', 'telefono']
    search_fields = ['user__username', 'nombre', 'cedula']


@admin.register(Emergencia)
class EmergenciaAdmin(admin.ModelAdmin):
    list_display = ['perfil', 'nombre', 'relacion', 'telefono']
    search_fields = ['perfil__user__username', 'nombre']


@admin.register(CambioPasswordAuditoria)
class CambioPasswordAuditoriaAdmin(admin.ModelAdmin):
    list_display = ['usuario_modificado', 'administrador', 'fecha_cambio', 'ip_address']
    list_filter = ['fecha_cambio']
    search_fields = ['usuario_modificado__username', 'administrador__username']
    readonly_fields = ['usuario_modificado', 'administrador', 'fecha_cambio', 'ip_address', 'motivo']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Solo superusuarios pueden eliminar registros de auditoría
        return request.user.is_superuser
