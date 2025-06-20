from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class Categoria(models.Model):
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
    id_producto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    id_categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_categoria')
    id_proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_proveedor')
    id_marca = models.ForeignKey(Marca, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_marca')
    
    class Meta:
        db_table = 'producto'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
    
    def __str__(self):
        return self.nombre

class Cliente(models.Model):
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
    id_stock = models.AutoField(primary_key=True)
    id_producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_producto')
    cantidad = models.IntegerField(null=True, blank=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'stock'
        verbose_name = 'Stock'
        verbose_name_plural = 'Stocks'
    
    def __str__(self):
        return f"Stock {self.id_producto} - {self.cantidad}"

class Nomina(models.Model):
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
    id_reporte = models.ForeignKey(Reportes, on_delete=models.CASCADE, db_column='id_reporte')
    id_factura = models.ForeignKey(Facturacion, on_delete=models.CASCADE, db_column='id_factura')
    
    class Meta:
        db_table = 'reporte_facturas'
        unique_together = (('id_reporte', 'id_factura'),)

class ReporteCompras(models.Model):
    id_reporte = models.ForeignKey(Reportes, on_delete=models.CASCADE, db_column='id_reporte')
    id_compra = models.ForeignKey(Compra, on_delete=models.CASCADE, db_column='id_compra')
    
    class Meta:
        db_table = 'reporte_compras'
        unique_together = (('id_reporte', 'id_compra'),)

class ReporteGastos(models.Model):
    id_reporte = models.ForeignKey(Reportes, on_delete=models.CASCADE, db_column='id_reporte')
    id_gasto = models.ForeignKey(MovimientosFinancieros, on_delete=models.CASCADE, db_column='id_gasto')
    
    class Meta:
        db_table = 'reporte_gastos'
        unique_together = (('id_reporte', 'id_gasto'),)

class ReporteNomina(models.Model):
    id_reporte = models.ForeignKey(Reportes, on_delete=models.CASCADE, db_column='id_reporte')
    id_nomina = models.ForeignKey(Nomina, on_delete=models.CASCADE, db_column='id_nomina')
    
    class Meta:
        db_table = 'reporte_nomina'
        unique_together = (('id_reporte', 'id_nomina'),)

class ReporteStock(models.Model):
    id_reporte = models.ForeignKey(Reportes, on_delete=models.CASCADE, db_column='id_reporte')
    id_stock = models.ForeignKey(Stock, on_delete=models.CASCADE, db_column='id_stock')
    
    class Meta:
        db_table = 'reporte_stock'
        unique_together = (('id_reporte', 'id_stock'),)