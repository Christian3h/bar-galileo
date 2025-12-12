from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100, blank=True)
    cedula = models.CharField(max_length=20, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.CharField(max_length=200, blank=True)
    avatar = models.ImageField(upload_to='img/avatar/', null=True, blank=True)

class Emergencia(models.Model):
    perfil = models.OneToOneField(PerfilUsuario, on_delete=models.CASCADE, related_name='emergencia')
    nombre = models.CharField(max_length=100, blank=True)
    relacion = models.CharField(max_length=50, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    telefono_alt = models.CharField(max_length=20, blank=True)
    sangre = models.CharField(max_length=10, blank=True)
    alergias = models.CharField(max_length=200, blank=True)

class CambioPasswordAuditoria(models.Model):
    """Registro de auditoría para cambios de contraseña por administradores"""
    usuario_modificado = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cambios_password')
    administrador = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='cambios_password_realizados')
    fecha_cambio = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    motivo = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-fecha_cambio']
        verbose_name = 'Auditoría de Cambio de Contraseña'
        verbose_name_plural = 'Auditorías de Cambios de Contraseña'
    
    def __str__(self):
        return f"{self.usuario_modificado.username} - Cambiado por {self.administrador.username if self.administrador else 'Sistema'} - {self.fecha_cambio.strftime('%d/%m/%Y %H:%M')}"
