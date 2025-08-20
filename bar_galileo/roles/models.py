from django.db import models
from django.contrib.auth.models import User

class Module(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

class Action(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

class Role(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

class RolePermission(models.Model):
    rol = models.ForeignKey(Role, on_delete=models.CASCADE)
    modulo = models.ForeignKey(Module, on_delete=models.CASCADE)
    accion = models.ForeignKey(Action, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('rol', 'modulo', 'accion')

    def __str__(self):
        return f"{self.rol} | {self.modulo} | {self.accion}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.rol.nombre if self.rol else 'Sin rol'}"
