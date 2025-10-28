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

    # Relación con usuario del sistema (opcional para no romper datos existentes)
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='empleado',
        verbose_name="Usuario del sistema"
    )

    nombre = models.CharField(max_length=100, verbose_name="Nombre completo")
    cargo = models.CharField(max_length=100, verbose_name="Cargo", blank=True, null=True, help_text="Descripción del cargo (se usa el rol del usuario si está vinculado)")
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

    @property
    def tiene_usuario(self):
        """Verifica si el empleado tiene usuario vinculado"""
        return self.user is not None

    @property
    def usuario_activo(self):
        """Verifica si el usuario vinculado está activo"""
        return self.user and self.user.is_active if self.tiene_usuario else False

    def get_cargo_display(self):
        """Retorna el cargo: del rol del usuario si existe, sino el campo cargo"""
        if self.user and hasattr(self.user, 'userprofile') and self.user.userprofile.rol:
            return self.user.userprofile.rol.nombre
        return self.cargo or "Sin cargo asignado"

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
    
    # Auditoría
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pagos_creados',
        verbose_name="Creado por"
    )
    modified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pagos_modificados',
        verbose_name="Modificado por"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name="Última modificación")

    class Meta:
        ordering = ['-fecha_pago']
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"

    def __str__(self):
        return f"Pago a {self.empleado.nombre} - {self.fecha_pago} - ${self.monto}"

class Bonificacion(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='bonificaciones', verbose_name="Empleado")
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    monto = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto")
    recurrente = models.BooleanField(default=False, verbose_name="¿Es recurrente?")
    fecha_inicio = models.DateField(verbose_name="Fecha de inicio")
    fecha_fin = models.DateField(blank=True, null=True, verbose_name="Fecha de finalización (opcional)")
    activa = models.BooleanField(default=True, verbose_name="Activa")
    
    # Auditoría
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bonificaciones_creadas',
        verbose_name="Creado por"
    )
    modified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bonificaciones_modificadas',
        verbose_name="Modificado por"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name="Última modificación")

    class Meta:
        ordering = ['-fecha_inicio']
        verbose_name = "Bonificación"
        verbose_name_plural = "Bonificaciones"

    def __str__(self):
        return f"{self.nombre} - {self.empleado.nombre} - ${self.monto}"
    
    def clean(self):
        """Validar fechas de bonificación"""
        from django.core.exceptions import ValidationError
        if self.fecha_fin and self.fecha_inicio > self.fecha_fin:
            raise ValidationError("La fecha de fin no puede ser anterior a la fecha de inicio")
    
    @property
    def esta_vigente(self):
        """Verifica si la bonificación está vigente"""
        if not self.activa:
            return False
        hoy = timezone.now().date()
        if self.fecha_fin:
            return self.fecha_inicio <= hoy <= self.fecha_fin
        return self.fecha_inicio <= hoy