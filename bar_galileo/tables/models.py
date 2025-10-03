<<<<<<< HEAD
from django.db import models
from django.utils import timezone
from products.models import Producto
from django.contrib.auth.models import User

class Mesa(models.Model):
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('ocupada', 'Ocupada'),
        ('reservada', 'Reservada'),
        ('fuera de servicio', 'Fuera de servicio'),
    ]
    
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='disponible')

    def __str__(self):
        return self.nombre

class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('en_proceso', 'En Proceso'),
        ('facturado', 'Facturado'),
        ('cancelado', 'Cancelado'),
    ]

    mesa = models.ForeignKey(Mesa, on_delete=models.SET_NULL, related_name='pedidos', null=True, blank=True)
    usuarios = models.ManyToManyField(User, related_name='pedidos_asociados', blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='en_proceso')
    
    def total(self):
        return sum(item.subtotal() for item in self.items.all())

    def __str__(self):
        mesa_info = f"Mesa {self.mesa.nombre}" if self.mesa else "Sin mesa"
        return f'Pedido {self.id} - {mesa_info}'

class PedidoItem(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f'{self.cantidad}x {self.producto.nombre}'

class Factura(models.Model):
    pedido = models.OneToOneField(Pedido, on_delete=models.PROTECT, related_name='factura')
    numero = models.CharField(max_length=20, unique=True)
    fecha = models.DateTimeField(default=timezone.now)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f'Factura #{self.numero}'

    def save(self, *args, **kwargs):
        if not self.numero:
            # Fetch only the 'numero' field to avoid loading potentially corrupt data in other fields.
            last_numero = Factura.objects.order_by('-id').values_list('numero', flat=True).first()
            next_number = '1' if not last_numero else str(int(last_numero) + 1)
            self.numero = next_number.zfill(8)
        
        # Check for None specifically to handle totals that are 0.
        if self.total is None:
            self.total = self.pedido.total()
        super().save(*args, **kwargs)
=======
from django.db import models
from django.utils import timezone
from products.models import Producto

class Mesa(models.Model):
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('ocupada', 'Ocupada'),
        ('reservada', 'Reservada'),
        ('fuera de servicio', 'Fuera de servicio'),
    ]
    
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='disponible')

    def __str__(self):
        return self.nombre

class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('en_proceso', 'En Proceso'),
        ('facturado', 'Facturado'),
        ('cancelado', 'Cancelado'),
    ]

    mesa = models.ForeignKey(Mesa, on_delete=models.SET_NULL, related_name='pedidos', null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='en_proceso')
    
    def total(self):
        return sum(item.subtotal() for item in self.items.all())

    def __str__(self):
        mesa_info = f"Mesa {self.mesa.nombre}" if self.mesa else "Sin mesa"
        return f'Pedido {self.id} - {mesa_info}'

class PedidoItem(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    
    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f'{self.cantidad}x {self.producto.nombre}'

class Factura(models.Model):
    pedido = models.OneToOneField(Pedido, on_delete=models.PROTECT, related_name='factura')
    numero = models.CharField(max_length=20, unique=True)
    fecha = models.DateTimeField(default=timezone.now)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f'Factura #{self.numero}'

    def save(self, *args, **kwargs):
        if not self.numero:
            last_factura = Factura.objects.order_by('-id').first()
            next_number = '1' if not last_factura else str(int(last_factura.numero) + 1)
            self.numero = next_number.zfill(8)
        if not self.total:
            self.total = self.pedido.total()
        super().save(*args, **kwargs)
>>>>>>> f550aac13c0202e2f4652738b7d329dd256a899a
