from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from django.contrib.auth.models import User

class Empleado(models.Model):
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('vacaciones', 'Vacaciones'),
        ('permiso', 'Permiso'),
        ('suspendido', 'Suspendido'),
    ]
    
    TIPO_CONTRATO_CHOICES = [
        ('tiempo_completo', 'Tiempo Completo'),
        ('medio_tiempo', 'Medio Tiempo'),
        ('temporal', 'Temporal'),
        ('por_proyecto', 'Por Proyecto'),
    ]
    
    # Relación con el usuario del sistema (NUEVO)
    usuario = models.OneToOneField(
        User, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='empleado_nomina',
        verbose_name="Usuario del sistema",
        help_text="Conectar con un usuario existente del sistema (opcional)"
    )
    
    nombre = models.CharField(max_length=100, verbose_name="Nombre completo")
    cargo = models.CharField(max_length=100, verbose_name="Cargo")
    salario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Salario base")
    fecha_contratacion = models.DateField(verbose_name="Fecha de contratación")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo', verbose_name="Estado")
    tipo_contrato = models.CharField(max_length=20, choices=TIPO_CONTRATO_CHOICES, default='tiempo_completo', verbose_name="Tipo de contrato")
    email = models.EmailField(max_length=100, blank=True, null=True, verbose_name="Correo electrónico")
    telefono = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="El número debe estar en formato: '+999999999'")],
        verbose_name="Teléfono"
    )
    direccion = models.TextField(blank=True, null=True, verbose_name="Dirección")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última actualización")

    class Meta:
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"
        ordering = ['-fecha_contratacion']

    def __str__(self):
        return f"{self.nombre} - {self.cargo}"
    
    def get_salario_total(self):
        """Calcula el salario total incluyendo bonificaciones"""
        return self.salario + sum(bonificacion.monto for bonificacion in self.bonificaciones.all())
    
    @property
    def antiguedad(self):
        """Calcula la antigüedad del empleado en años"""
        today = timezone.now().date()
        return (today - self.fecha_contratacion).days // 365
    
    def sincronizar_con_usuario(self):
        """Sincroniza los datos del empleado con su usuario del sistema"""
        if self.usuario:
            # Actualizar información del empleado desde el usuario
            if self.usuario.first_name and self.usuario.last_name:
                self.nombre = f"{self.usuario.first_name} {self.usuario.last_name}"
            if self.usuario.email:
                self.email = self.usuario.email
            
            # Actualizar desde el perfil si existe
            if hasattr(self.usuario, 'perfilusuario'):
                perfil = self.usuario.perfilusuario
                if perfil.telefono:
                    self.telefono = perfil.telefono
                if perfil.direccion:
                    self.direccion = perfil.direccion

class Pago(models.Model):
    TIPO_CHOICES = [
        ('salario', 'Salario'),
        ('bono', 'Bonificación'),
        ('vacaciones', 'Pago Vacaciones'),
        ('liquidacion', 'Liquidación'),
        ('otro', 'Otro'),
    ]
    
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='pagos', verbose_name="Empleado")
    fecha_pago = models.DateField(default=timezone.now, verbose_name="Fecha de pago")
    monto = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='salario', verbose_name="Tipo de pago")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    comprobante = models.FileField(upload_to='nominas/comprobantes/', blank=True, null=True, verbose_name="Comprobante")
    
    def __str__(self):
        return f"Pago a {self.empleado.nombre} - {self.fecha_pago} - ${self.monto}"

class Bonificacion(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='bonificaciones', verbose_name="Empleado")
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    monto = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto")
    recurrente = models.BooleanField(default=False, verbose_name="¿Es recurrente?")
    fecha_inicio = models.DateField(verbose_name="Fecha de inicio")
    fecha_fin = models.DateField(blank=True, null=True, verbose_name="Fecha de finalización (opcional)")
    
    def __str__(self):
        return f"{self.nombre} - {self.empleado.nombre} - ${self.monto}"