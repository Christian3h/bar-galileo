# Modelo del sistema de reportes. Flujo: crear reporte → generar datos → exportar.

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import json


class Reporte(models.Model):
    # Guarda la configuración del reporte (tipo, fechas, formato) y los datos generados en caché como JSON.
    # Tipo del reporte → determina qué función de utils.py se llama para obtener los datos
    TIPO_CHOICES = [
        ('ventas', 'Ventas'),
        ('inventario', 'Inventario'),
        ('gastos', 'Gastos'),
        ('nominas', 'Nóminas'),
        ('productos', 'Productos'),
        ('mesas', 'Mesas y Pedidos'),
        ('general', 'General'),
    ]
    
    # Periodo informativo; el filtrado real usa fecha_inicio y fecha_fin
    PERIODO_CHOICES = [
        ('diario', 'Diario'),
        ('semanal', 'Semanal'),
        ('mensual', 'Mensual'),
        ('trimestral', 'Trimestral'),
        ('anual', 'Anual'),
        ('personalizado', 'Personalizado'),
    ]
    
    # Formato de exportación: pdf=reportlab, excel=openpyxl, csv=stdlib
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
    datos_json = models.TextField(blank=True, null=True, verbose_name='Datos del Reporte (JSON)')
    ultima_generacion = models.DateTimeField(null=True, blank=True, verbose_name='Última Generación')
    
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
        # Días que cubre el reporte (incluye ambos extremos: un solo día = 1, no 0)
        if self.fecha_inicio and self.fecha_fin:
            return (self.fecha_fin - self.fecha_inicio).days + 1
        return 0
    
    @property
    def esta_vencido(self):
        # True si el reporte fue creado hace más de 30 días (señal para regenerar)
        if self.fecha_creacion:
            return (timezone.now() - self.fecha_creacion).days > 30
        return False
    
    def get_datos(self):
        # Lee datos_json y lo deserializa; devuelve {} si está vacío o malformado
        if self.datos_json:
            try:
                return json.loads(self.datos_json)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_datos(self, datos):
        # Serializa el dict de datos a JSON y actualiza ultima_generacion; llama .save() después
        self.datos_json = json.dumps(datos, ensure_ascii=False)
        self.ultima_generacion = timezone.now()
