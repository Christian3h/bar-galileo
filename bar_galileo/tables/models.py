from django.db import models

class Mesa(models.Model):
    ESTADOS = [
        ('disponible', 'Disponible'),
        ('ocupada', 'Ocupada'),
        ('reservada', 'Reservada'),
        ('fuera de servicio', 'Fuera de servicio'),
    ]

    nombre = models.CharField(max_length=50)
    descripcion = models.TextField()
    estado = models.CharField(max_length=50, choices=ESTADOS, default='disponible')

    def __str__(self):
        return f"{self.nombre} - {self.get_estado_display()}"
