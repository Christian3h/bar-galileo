"""
Modelos principales del sistema Bar Galileo.
Cada clase representa una tabla en la base de datos y define sus relaciones y restricciones.
"""


from django.db import models
from django.core.exceptions import ValidationError
from PIL import Image
from io import BytesIO
from django.conf import settings
from PIL import Image
from io import BytesIO
import os




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
    Las imágenes se guardan en media/productos/{id_producto}/
    """
    name, _ = os.path.splitext(filename)
    # Siempre guardar como .webp
    filename = f"{name}.webp"
    return f'productos/{instance.producto.id_producto}/{filename}'

class Categoria(models.Model):
    """
    Categoría de productos.
    - nombre_categoria: nombre de la categoría.
    - descripcion: descripción opcional.
    """
    id_categoria = models.AutoField(primary_key=True)
    nombre_categoria = models.CharField(max_length=50, null=True, blank=True)
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
    marca = models.CharField(max_length=50)
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
    nombre = models.CharField(max_length=50)
    contacto = models.CharField(max_length=50)
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
    nombre = models.CharField(max_length=50, unique=True)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    id_categoria = models.ForeignKey('Categoria', on_delete=models.SET_NULL, null=True, blank=True)
    id_proveedor = models.ForeignKey('Proveedor', on_delete=models.SET_NULL, null=True, blank=True)
    id_marca = models.ForeignKey('Marca', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'producto'

    def stock_actual(self):
        """Obtiene el stock actual desde la tabla Stock"""
        ultimo_stock = self.stocks.order_by('-fecha_hora').first()
        if ultimo_stock:
            return ultimo_stock.cantidad
        return self.stock or 0

    def __str__(self):
        return self.nombre

    def clean(self):
        # Validar que el nombre no esté vacío
        if not self.nombre or not self.nombre.strip():
            raise ValidationError({'nombre': 'El nombre no puede estar vacío.'})

        # Validar que el precio de venta sea mayor que el de compra
        if self.precio_venta <= self.precio_compra:
            raise ValidationError({
                'precio_venta': 'El precio de venta debe ser mayor que el de compra.'
            })

        # Validar que el stock no sea negativo
        if self.stock is not None and self.stock < 0:
            raise ValidationError({'stock': 'El stock no puede ser negativo.'})

    def save(self, *args, **kwargs):
        # Validaciones previas
        self.full_clean()

        # Determinar si cambió el stock respecto a la instancia previa
        stock_cambio = False
        if self.pk:
            try:
                old_instance = Producto.objects.get(pk=self.pk)
                stock_cambio = old_instance.stock != self.stock
            except Producto.DoesNotExist:
                stock_cambio = True
        else:
            stock_cambio = self.stock is not None

        # Guardar instancia
        super().save(*args, **kwargs)

        # Registrar movimiento de stock si aplica
        if stock_cambio:
            Stock.objects.create(
                id_producto=self,
                cantidad=self.stock or 0
            )

# MODELO PARA IMÁGENES
class ProductoImagen(models.Model):
    id_imagen = models.AutoField(primary_key=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='imagenes')
    # Cambio de CharField a ImageField para usar MEDIA en lugar de STATIC
    imagen = models.ImageField(
        upload_to=producto_image_path,
        help_text='Imagen del producto (se guardará en media/productos/)'
    )

    class Meta:
        db_table = 'producto_imagen'
        verbose_name = 'Imagen del producto'
        verbose_name_plural = 'Imágenes de productos'

    def __str__(self):
        return f"Imagen {self.id_imagen} - {self.producto.nombre}"

def procesar_y_guardar_imagen(file, producto_id, nombre_base):
    """
    Procesa y guarda una imagen en formato WEBP en la carpeta media/productos/
    Retorna la ruta relativa para guardar en el modelo ProductoImagen
    """
    img = Image.open(file)
    img = img.convert('RGBA') if img.mode in ('RGBA', 'LA') else img.convert('RGB')

    buffer = BytesIO()
    img.save(buffer, format='WEBP', quality=85)

    # Ahora se guarda en MEDIA en lugar de STATIC
    carpeta = os.path.join(settings.MEDIA_ROOT, 'productos', str(producto_id))
    os.makedirs(carpeta, exist_ok=True)

    filename = f"{nombre_base}.webp"
    path_final = os.path.join(carpeta, filename)

    with open(path_final, 'wb') as f:
        f.write(buffer.getvalue())

    # Ruta relativa desde MEDIA_ROOT
    ruta_relativa = f"productos/{producto_id}/{filename}"
    return ruta_relativa

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
