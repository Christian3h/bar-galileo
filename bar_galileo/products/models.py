"""
Modelos principales del sistema Bar Galileo.
Cada clase representa una tabla en la base de datos y define sus relaciones y restricciones.
"""

from django.db import models
from django.core.validators import MinValueValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
import os
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.core.files.storage import default_storage
import shutil
import threading
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

def validate_image_file(file):
    """
    Validador personalizado para asegurar que solo se suban archivos PNG, JPG, JPEG o WEBP.
    """
    valid_exts = ['.png', '.jpg', '.jpeg', '.webp']
    valid_mimes = ['image/png', 'image/jpeg', 'image/webp']
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in valid_exts:
        raise ValidationError('Solo se permiten archivos PNG, JPG, JPEG o WEBP.')
    if hasattr(file, 'content_type') and file.content_type not in valid_mimes:
        raise ValidationError('El archivo debe ser una imagen PNG, JPG, JPEG o WEBP válida.')

def producto_image_path(instance, filename):
    """
    Genera la ruta para guardar la imagen del producto en formato webp.
    """
    name, _ = os.path.splitext(filename)
    # Siempre guardar como .webp
    filename = f"{name}.webp"
    return f'productos/{instance.id_producto}/{filename}'

class Categoria(models.Model):
    """
    Categoría de productos.
    - nombre_categoria: nombre de la categoría.
    - descripcion: descripción opcional.
    """
    id_categoria = models.AutoField(primary_key=True)
    nombre_categoria = models.CharField(max_length=100, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'categoria'
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
    
    def __str__(self):
        return self.nombre_categoria or f"Categoría {self.id_categoria}"

class Marca(models.Model):
    """
    Marca de productos.
    - marca: nombre de la marca.
    - descripcion: descripción opcional.
    """
    id_marca = models.AutoField(primary_key=True)
    marca = models.CharField(max_length=100)
    descripcion = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'marca'
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'
    
    def __str__(self):
        return self.marca

class Proveedor(models.Model):
    """
    Proveedor de productos.
    - nombre: nombre del proveedor.
    - contacto: persona de contacto.
    - telefono: teléfono de contacto.
    - direccion: dirección del proveedor.
    """
    id_proveedor = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    contacto = models.CharField(max_length=100)
    telefono = models.BigIntegerField(null=True, blank=True)
    direccion = models.TextField()
    
    class Meta:
        db_table = 'proveedor'
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
    
    def __str__(self):
        return self.nombre

class Producto(models.Model):
    """
    Producto del bar.
    - nombre: nombre del producto.
    - precio: precio unitario (obsoleto, usar precio_venta y precio_compra).
    - precio_compra: precio de compra del producto.
    - precio_venta: precio de venta del producto.
    - stock: cantidad disponible en stock.
    - descripcion: descripción detallada del producto.
    - id_categoria: relación con la categoría.
    - id_proveedor: relación con el proveedor.
    - id_marca: relación con la marca.
    - imagen: foto del producto (solo PNG).
    """
    id_producto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    id_categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_categoria')
    id_proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_proveedor')
    id_marca = models.ForeignKey(Marca, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_marca')
    imagen = models.ImageField(
        upload_to=producto_image_path,
        validators=[
            FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'webp']),
            validate_image_file
        ],
        null=True,
        blank=True,
        help_text="Solo se permiten archivos PNG, JPG, JPEG o WEBP"
    )
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], null=True, blank=True, help_text="Precio de compra del producto")
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], null=True, blank=True, help_text="Precio de venta del producto")
    stock = models.IntegerField(validators=[MinValueValidator(0)], null=True, blank=True, help_text="Cantidad disponible en stock")
    descripcion = models.TextField(null=True, blank=True, help_text="Descripción detallada del producto")
    
    class Meta:
        db_table = 'producto'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
    
    def __str__(self):
        return self.nombre
    
    def delete(self, *args, **kwargs):
        # Eliminar el archivo físico al eliminar el producto
        if self.imagen:
            imagen_path = self.imagen.path
            carpeta = os.path.dirname(imagen_path)
            if os.path.isfile(imagen_path):
                os.remove(imagen_path)
            # Eliminar la carpeta si queda vacía
            try:
                if os.path.isdir(carpeta) and not os.listdir(carpeta):
                    shutil.rmtree(carpeta)
            except Exception:
                pass
        super().delete(*args, **kwargs)
    
    # Variable de contexto de thread para evitar recursión infinita
    _stock_signal_context = threading.local()

    def save(self, *args, **kwargs):
        # Si se está eliminando la imagen (por edición), borra el archivo y la carpeta si queda vacía
        if self.pk:
            try:
                old = Producto.objects.get(pk=self.pk)
                if old.imagen and not self.imagen:
                    imagen_path = old.imagen.path
                    carpeta = os.path.dirname(imagen_path)
                    if os.path.isfile(imagen_path):
                        os.remove(imagen_path)
                    try:
                        if os.path.isdir(carpeta) and not os.listdir(carpeta):
                            shutil.rmtree(carpeta)
                    except Exception:
                        pass
            except Producto.DoesNotExist:
                pass
        # Convertir imagen a WebP si se sube una nueva imagen
        if self.imagen and hasattr(self.imagen, 'file'):
            try:
                img = Image.open(self.imagen)
                if img.format != 'WEBP':
                    img = img.convert('RGBA') if img.mode in ('RGBA', 'LA') else img.convert('RGB')
                    buffer = BytesIO()
                    img.save(buffer, format='WEBP', quality=85)
                    name = os.path.splitext(self.imagen.name)[0] + '.webp'
                    self.imagen.save(name, ContentFile(buffer.getvalue()), save=False)
                    print(f"[CONVERSIÓN] Imagen convertida a WebP: {name}")
                    # Eliminar el archivo original si existe y es diferente
                    original_path = os.path.join('media', self.imagen.name)
                    if os.path.exists(original_path) and not self.imagen.name.endswith('.webp'):
                        os.remove(original_path)
            except Exception as e:
                print(f"[ERROR] Falló la conversión a WebP: {e}")
        # Sincronizar el stock en la tabla Stock
        super().save(*args, **kwargs)
        from .models import Stock
        if self.stock is not None:
            stock_obj, created = Stock.objects.get_or_create(id_producto=self)
            if stock_obj.cantidad != self.stock:
                stock_obj.cantidad = self.stock
                stock_obj.save()

# Variable de contexto para evitar recursión infinita entre señal y save()
_stock_signal_context = threading.local()

# Señal para eliminar la imagen física cuando se borra un producto desde un queryset
@receiver(post_delete, sender=Producto)
def eliminar_imagen_producto(sender, instance, **kwargs):
    if instance.imagen:
        # Eliminar la imagen
        if default_storage.exists(instance.imagen.name):
            default_storage.delete(instance.imagen.name)
        # Eliminar la carpeta si está vacía
        carpeta = os.path.dirname(instance.imagen.path)
        try:
            if os.path.isdir(carpeta) and not os.listdir(carpeta):
                shutil.rmtree(carpeta)
        except Exception:
            pass

class Cliente(models.Model):
    """
    Cliente del bar.
    - nombre, apellido, correo, teléfono, dirección.
    """
    id_cliente = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    correo = models.EmailField(max_length=150, unique=True)
    telefono = models.BigIntegerField(null=True, blank=True)
    direccion = models.TextField()
    
    class Meta:
        db_table = 'cliente'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        constraints = [
            models.UniqueConstraint(fields=['correo'], name='uq_cliente_correo')
        ]
    
    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class Empleado(models.Model):
    """
    Empleado del bar.
    - nombre, apellido, cargo, correo, teléfono.
    """
    CARGO_CHOICES = [
        ('Mesera', 'Mesera'),
        ('Barman', 'Barman'),
        ('Cajera', 'Cajera'),
        ('Administrador', 'Administrador'),
    ]
    
    id_empleado = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    cargo = models.CharField(max_length=20, choices=CARGO_CHOICES)
    correo = models.EmailField(max_length=150, unique=True)
    telefono = models.BigIntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'empleado'
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'
        constraints = [
            models.UniqueConstraint(fields=['correo'], name='uq_empleado_correo')
        ]
    
    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.cargo}"

class Mesas(models.Model):
    """
    Mesa disponible en el bar.
    - numero_mesa: número identificador.
    - ubicacion: ubicación física.
    - cantidad_sillas: número de sillas.
    """
    id_mesa = models.AutoField(primary_key=True)
    numero_mesa = models.IntegerField()
    ubicacion = models.CharField(max_length=100, null=True, blank=True)
    cantidad_sillas = models.IntegerField()
    
    class Meta:
        db_table = 'mesas'
        verbose_name = 'Mesa'
        verbose_name_plural = 'Mesas'
    
    def __str__(self):
        return f"Mesa {self.numero_mesa} - {self.ubicacion}"

class TipoPago(models.Model):
    """
    Métodos de pago aceptados.
    - metodo: tipo de pago (efectivo, tarjeta, etc).
    """
    METODOS_PAGO = [
        ('Efectivo', 'Efectivo'),
        ('Tarjeta de crédito', 'Tarjeta de crédito'),
        ('Nequi', 'Nequi'),
        ('Transferencia', 'Transferencia'),
    ]
    
    id_tipo_pago = models.IntegerField(primary_key=True)
    metodo = models.CharField(max_length=20, choices=METODOS_PAGO)
    
    class Meta:
        db_table = 'tipo_pago'
        verbose_name = 'Tipo de Pago'
        verbose_name_plural = 'Tipos de Pago'
    
    def __str__(self):
        return self.metodo

class Pedido(models.Model):
    """
    Pedido realizado por un cliente.
    - fecha, cliente, empleado, mesa.
    """
    id_pedido = models.AutoField(primary_key=True)
    fecha = models.DateField(null=True, blank=True)
    id_cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_cliente')
    id_empleado = models.ForeignKey(Empleado, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_empleado')
    id_mesa = models.ForeignKey(Mesas, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_mesa')
    
    class Meta:
        db_table = 'pedido'
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
    
    def __str__(self):
        return f"Pedido {self.id_pedido} - {self.fecha}"

class DetallePedido(models.Model):
    """
    Detalle de cada producto en un pedido.
    - pedido, producto, cantidad.
    """
    id_detalle = models.IntegerField(primary_key=True)
    id_pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, null=True, blank=True, db_column='id_pedido')
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE, null=True, blank=True, db_column='id_producto')
    cantidad = models.IntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'detalle_pedido'
        verbose_name = 'Detalle de Pedido'
        verbose_name_plural = 'Detalles de Pedidos'
    
    def __str__(self):
        return f"Detalle {self.id_detalle} - Pedido {self.id_pedido}"

class Facturacion(models.Model):
    """
    Factura generada para un pedido.
    - pedido, total, fecha, tipo de pago.
    """
    id_factura = models.AutoField(primary_key=True)
    id_pedido = models.ForeignKey(Pedido, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_pedido')
    total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fecha = models.DateField(null=True, blank=True)
    id_tipo_pago = models.ForeignKey(TipoPago, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_tipo_pago')
    
    class Meta:
        db_table = 'facturacion'
        verbose_name = 'Facturación'
        verbose_name_plural = 'Facturaciones'
    
    def __str__(self):
        return f"Factura {self.id_factura} - ${self.total}"

class DescuentosPedido(models.Model):
    """
    Descuentos aplicados a un pedido.
    - descripcion, porcentaje, pedido.
    """
    id_descuento = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=255, null=True, blank=True)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    id_pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, null=True, blank=True, db_column='id_pedido')
    
    class Meta:
        db_table = 'descuentos_pedido'
        verbose_name = 'Descuento de Pedido'
        verbose_name_plural = 'Descuentos de Pedidos'
    
    def __str__(self):
        return f"{self.descripcion} - {self.porcentaje}%"

class Compra(models.Model):
    """
    Registro de compras de inventario.
    - producto, cantidad, fecha, proveedor, empleado.
    """
    id_inventario = models.AutoField(primary_key=True)
    id_producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_producto')
    cantidad_actual = models.IntegerField(null=True, blank=True)
    fecha_recibido = models.DateField()
    novedades = models.TextField(null=True, blank=True)
    id_proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_proveedor')
    id_empleado = models.ForeignKey(Empleado, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_empleado')
    
    class Meta:
        db_table = 'compra'
        verbose_name = 'Compra'
        verbose_name_plural = 'Compras'
    
    def __str__(self):
        return f"Compra {self.id_inventario} - {self.fecha_recibido}"

class Stock(models.Model):
    """
    Stock actual de un producto.
    - producto, cantidad, fecha/hora.
    """
    id_stock = models.AutoField(primary_key=True)
    id_producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_producto', related_name='stocks')
    cantidad = models.IntegerField(null=True, blank=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'stock'
        verbose_name = 'Stock'
        verbose_name_plural = 'Stocks'
    
    def __str__(self):
        return f"Stock {self.id_producto} - {self.cantidad}"

class Nomina(models.Model):
    """
    Nómina de empleados.
    - empleado, salario base, fecha de pago.
    """
    id_nomina = models.AutoField(primary_key=True)
    id_empleado = models.ForeignKey(Empleado, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_empleado')
    salario_base = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fecha_pago = models.DateField(null=True, blank=True)
    
    class Meta:
        db_table = 'nomina'
        verbose_name = 'Nómina'
        verbose_name_plural = 'Nóminas'
    
    def __str__(self):
        return f"Nómina {self.id_empleado} - {self.fecha_pago}"

class MovimientosFinancieros(models.Model):
    """
    Movimientos financieros (ingresos y egresos).
    - descripcion, monto, tipo, recibo, empleado, fecha.
    """
    TIPO_CHOICES = [
        ('Ingreso', 'Ingreso'),
        ('Egreso', 'Egreso'),
    ]
    
    id_gasto = models.AutoField(primary_key=True)
    descripcion = models.TextField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    recibo = models.CharField(max_length=100, null=True, blank=True)
    id_empleado = models.ForeignKey(Empleado, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_empleado')
    fecha = models.DateField()
    
    class Meta:
        db_table = 'movimientos_financieros'
        verbose_name = 'Movimiento Financiero'
        verbose_name_plural = 'Movimientos Financieros'
    
    def __str__(self):
        return f"{self.tipo} - ${self.monto} - {self.fecha}"

class Reportes(models.Model):
    """
    Reportes generados por el sistema.
    - descripcion, tipo, fechas.
    """
    TIPO_REPORTE_CHOICES = [
        ('Ventas', 'Ventas'),
        ('Compras', 'Compras'),
        ('Gastos', 'Gastos'),
        ('Nomina', 'Nomina'),
        ('Existencias', 'Existencias'),
    ]
    
    id_reporte = models.AutoField(primary_key=True)
    descripcion = models.TextField(null=True, blank=True)
    tipo_reporte = models.CharField(max_length=15, choices=TIPO_REPORTE_CHOICES)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    fecha_generacion = models.DateField(null=True, blank=True)
    
    class Meta:
        db_table = 'reportes'
        verbose_name = 'Reporte'
        verbose_name_plural = 'Reportes'
    
    def __str__(self):
        return f"{self.tipo_reporte} - {self.fecha_generacion}"

# Tablas de relaciones many-to-many para reportes
class ReporteFacturas(models.Model):
    """
    Relación entre reportes y facturas.
    """
    id_reporte = models.ForeignKey(Reportes, on_delete=models.CASCADE, db_column='id_reporte')
    id_factura = models.ForeignKey(Facturacion, on_delete=models.CASCADE, db_column='id_factura')
    
    class Meta:
        db_table = 'reporte_facturas'
        unique_together = (('id_reporte', 'id_factura'),)

class ReporteCompras(models.Model):
    """
    Relación entre reportes y compras.
    """
    id_reporte = models.ForeignKey(Reportes, on_delete=models.CASCADE, db_column='id_reporte')
    id_compra = models.ForeignKey(Compra, on_delete=models.CASCADE, db_column='id_compra')
    
    class Meta:
        db_table = 'reporte_compras'
        unique_together = (('id_reporte', 'id_compra'),)

class ReporteGastos(models.Model):
    """
    Relación entre reportes y gastos.
    """
    id_reporte = models.ForeignKey(Reportes, on_delete=models.CASCADE, db_column='id_reporte')
    id_gasto = models.ForeignKey(MovimientosFinancieros, on_delete=models.CASCADE, db_column='id_gasto')
    
    class Meta:
        db_table = 'reporte_gastos'
        unique_together = (('id_reporte', 'id_gasto'),)

class ReporteNomina(models.Model):
    """
    Relación entre reportes y nómina.
    """
    id_reporte = models.ForeignKey(Reportes, on_delete=models.CASCADE, db_column='id_reporte')
    id_nomina = models.ForeignKey(Nomina, on_delete=models.CASCADE, db_column='id_nomina')
    
    class Meta:
        db_table = 'reporte_nomina'
        unique_together = (('id_reporte', 'id_nomina'),)

class ReporteStock(models.Model):
    """
    Relación entre reportes y stock.
    """
    id_reporte = models.ForeignKey(Reportes, on_delete=models.CASCADE, db_column='id_reporte')
    id_stock = models.ForeignKey(Stock, on_delete=models.CASCADE, db_column='id_stock')
    
    class Meta:
        db_table = 'reporte_stock'
        unique_together = (('id_reporte', 'id_stock'),)

def actualizar_stock_producto(sender, instance, created, **kwargs):
    """
    Cuando se crea un registro de Stock, actualiza el campo stock del producto relacionado sumando todos los movimientos.
    """
    if created and instance.id_producto:
        from .models import Stock
        total_stock = Stock.objects.filter(id_producto=instance.id_producto).aggregate(models.Sum('cantidad'))['cantidad__sum'] or 0
        _stock_signal_context.from_signal = True
        try:
            instance.id_producto.stock = total_stock
            instance.id_producto.save(update_fields=['stock'])
        finally:
            _stock_signal_context.from_signal = False

post_save.connect(actualizar_stock_producto, sender=Stock)

# Señal para sincronizar el stock de Producto cuando se actualiza Stock
@receiver(post_save, sender=Stock)
def sincronizar_stock_producto(sender, instance, **kwargs):
    if instance.id_producto and instance.cantidad is not None:
        if instance.id_producto.stock != instance.cantidad:
            instance.id_producto.stock = instance.cantidad
            instance.id_producto.save(update_fields=['stock'])