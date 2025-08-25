from django.contrib.auth.models import User
from django.db import models

class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100, blank=True)
    cedula = models.CharField(max_length=20, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.CharField(max_length=200, blank=True)
    cliente_desde = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='img/avatar/', null=True, blank=True)

class Emergencia(models.Model):
    perfil = models.OneToOneField(PerfilUsuario, on_delete=models.CASCADE, related_name='emergencia')
    nombre = models.CharField(max_length=100, blank=True)
    relacion = models.CharField(max_length=50, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    telefono_alt = models.CharField(max_length=20, blank=True)
    sangre = models.CharField(max_length=10, blank=True)
    alergias = models.CharField(max_length=200, blank=True)
