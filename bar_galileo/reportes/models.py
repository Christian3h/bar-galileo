from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class Reporte(models.Model):
    """Modelo base para reportes generados"""
    TIPO_CHOICES = [
        ('ventas', 'Ventas'),
        ('inventario', 'Inventario'),
        ('gastos', 'Gastos'),
        ('nominas', 'Nóminas'),
        ('general', 'General'),
    ]
    
    PERIODO_CHOICES = [
        ('mensual', 'Mensual'),
        ('trimestral', 'Trimestral'),
        ('anual', 'Anual'),
        ('personalizado', 'Personalizado'),
    ]
    
    FORMATO_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
    ]
    
    nombre = models.CharField(max_length=200, verbose_name='Nombre del Reporte')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='general', verbose_name='Tipo de Reporte')
    periodo = models.CharField(max_length=20, choices=PERIODO_CHOICES, default='mensual', verbose_name='Periodo')
    formato = models.CharField(max_length=10, choices=FORMATO_CHOICES, default='pdf', verbose_name='Formato de Exportación')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reportes_creados')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    fecha_inicio = models.DateField(verbose_name='Fecha Inicio')
    fecha_fin = models.DateField(verbose_name='Fecha Fin')
    archivo = models.FileField(upload_to='reportes/', blank=True, null=True, verbose_name='Archivo')
    generado = models.BooleanField(default=False, verbose_name='Reporte Generado')
    
    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Reporte'
        verbose_name_plural = 'Reportes'
        permissions = [
            ('exportar_reporte', 'Puede exportar reportes'),
            ('generar_reporte', 'Puede generar reportes automáticamente'),
        ]
    
    def __str__(self):
        return f"{self.nombre} - {self.get_tipo_display()}"
    
    @property
    def duracion_dias(self):
        """Retorna la duración del periodo en días"""
        if self.fecha_inicio and self.fecha_fin:
            return (self.fecha_fin - self.fecha_inicio).days + 1
        return 0
    
    @property
    def esta_vencido(self):
        """Verifica si el reporte está desactualizado (más de 30 días)"""
        if self.fecha_creacion:
            return (timezone.now() - self.fecha_creacion).days > 30
        return False
