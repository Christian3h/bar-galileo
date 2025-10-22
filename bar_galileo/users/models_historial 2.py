from django.db import models
from users.models import PerfilUsuario

class HistorialMensual(models.Model):
    perfil = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE)
    mes = models.CharField(max_length=3)  # ej: 'ene', 'feb', ...
    total = models.IntegerField(null=True, blank=True)
    barras = models.JSONField(null=True, blank=True)  # lista de valores

    def __str__(self):
        return f"{self.perfil.user.username} - {self.mes}"
