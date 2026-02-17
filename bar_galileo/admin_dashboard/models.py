from django.db import models
from django.core.validators import FileExtensionValidator
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys
import os


class SiteImageSection(models.Model):
    """Secciones donde se pueden ubicar imágenes en el sitio"""
    SECTION_CHOICES = [
        ('hero_carousel', 'Carrusel Principal'),
        ('about', 'Sección Acerca de'),
        ('services', 'Servicios'),
        ('header', 'Encabezado'),
        ('footer', 'Pie de Página'),
        ('banner', 'Banner'),
        ('icon', 'Icono'),
        ('background', 'Fondo'),
        ('custom', 'Personalizado'),
    ]
    
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre de la sección")
    section_type = models.CharField(
        max_length=50, 
        choices=SECTION_CHOICES,
        verbose_name="Tipo de sección"
    )
    description = models.TextField(blank=True, verbose_name="Descripción")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Sección de Imagen"
        verbose_name_plural = "Secciones de Imágenes"
        ordering = ['section_type', 'name']
    
    def __str__(self):
        return f"{self.get_section_type_display()} - {self.name}"


class SiteImage(models.Model):
    """Imágenes generales del sitio web"""
    section = models.ForeignKey(
        SiteImageSection, 
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="Sección"
    )
    title = models.CharField(max_length=200, verbose_name="Título")
    image = models.ImageField(
        upload_to='site_images/%Y/%m/',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])],
        verbose_name="Imagen"
    )
    alt_text = models.CharField(max_length=255, blank=True, verbose_name="Texto alternativo")
    order = models.IntegerField(default=0, verbose_name="Orden")
    is_active = models.BooleanField(default=True, verbose_name="Activa")
    
    # Dimensiones para referencia
    width = models.IntegerField(null=True, blank=True, editable=False)
    height = models.IntegerField(null=True, blank=True, editable=False)
    file_size = models.IntegerField(null=True, blank=True, editable=False, verbose_name="Tamaño de archivo (bytes)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Imagen del Sitio"
        verbose_name_plural = "Imágenes del Sitio"
        ordering = ['section', 'order', '-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.section.name}"
    
    def save(self, *args, **kwargs):
        """Optimiza la imagen antes de guardar"""
        if self.image:
            # Abrir la imagen
            img = Image.open(self.image)
            
            # Guardar dimensiones originales
            self.width, self.height = img.size
            
            # Convertir RGBA a RGB si es necesario
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Redimensionar si es muy grande (máximo 2000px en cualquier dimensión)
            max_size = 2000
            if img.width > max_size or img.height > max_size:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Guardar la imagen optimizada
            output = BytesIO()
            
            # Determinar formato basado en la extensión
            image_format = 'JPEG'
            extension = os.path.splitext(self.image.name)[1].lower()
            if extension in ['.png']:
                image_format = 'PNG'
            elif extension in ['.webp']:
                image_format = 'WEBP'
            
            # Guardar con compresión
            if image_format == 'JPEG':
                img.save(output, format='JPEG', quality=85, optimize=True)
            elif image_format == 'PNG':
                img.save(output, format='PNG', optimize=True)
            elif image_format == 'WEBP':
                img.save(output, format='WEBP', quality=85, optimize=True)
            
            output.seek(0)
            
            # Guardar tamaño del archivo
            self.file_size = output.getbuffer().nbytes
            
            # Reemplazar el archivo
            self.image = InMemoryUploadedFile(
                output,
                'ImageField',
                self.image.name,
                f'image/{image_format.lower()}',
                sys.getsizeof(output),
                None
            )
        
        super().save(*args, **kwargs)
    
    def get_file_size_display(self):
        """Retorna el tamaño del archivo en formato legible"""
        if not self.file_size:
            return "N/A"
        
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"


class CarouselImage(models.Model):
    """Imágenes específicas para el carrusel principal"""
    title = models.CharField(max_length=200, verbose_name="Título")
    image = models.ImageField(
        upload_to='carousel/%Y/%m/',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])],
        verbose_name="Imagen"
    )
    alt_text = models.CharField(max_length=255, blank=True, verbose_name="Texto alternativo")
    caption = models.CharField(max_length=300, blank=True, verbose_name="Texto descriptivo")
    link_url = models.URLField(blank=True, verbose_name="URL de enlace")
    order = models.IntegerField(default=0, verbose_name="Orden")
    is_active = models.BooleanField(default=True, verbose_name="Activa")
    
    # Dimensiones para referencia
    width = models.IntegerField(null=True, blank=True, editable=False)
    height = models.IntegerField(null=True, blank=True, editable=False)
    file_size = models.IntegerField(null=True, blank=True, editable=False, verbose_name="Tamaño de archivo (bytes)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Imagen del Carrusel"
        verbose_name_plural = "Imágenes del Carrusel"
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return f"{self.title} (Orden: {self.order})"
    
    def save(self, *args, **kwargs):
        """Optimiza la imagen antes de guardar"""
        if self.image:
            # Abrir la imagen
            img = Image.open(self.image)
            
            # Guardar dimensiones originales
            self.width, self.height = img.size
            
            # Convertir RGBA a RGB si es necesario
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Para el carrusel, asegurar un tamaño adecuado (1920x1080 máximo)
            max_width = 1920
            max_height = 1080
            
            if img.width > max_width or img.height > max_height:
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Guardar la imagen optimizada
            output = BytesIO()
            
            # Determinar formato basado en la extensión
            image_format = 'JPEG'
            extension = os.path.splitext(self.image.name)[1].lower()
            if extension in ['.png']:
                image_format = 'PNG'
            elif extension in ['.webp']:
                image_format = 'WEBP'
            
            # Guardar con compresión
            if image_format == 'JPEG':
                img.save(output, format='JPEG', quality=85, optimize=True)
            elif image_format == 'PNG':
                img.save(output, format='PNG', optimize=True)
            elif image_format == 'WEBP':
                img.save(output, format='WEBP', quality=85, optimize=True)
            
            output.seek(0)
            
            # Guardar tamaño del archivo
            self.file_size = output.getbuffer().nbytes
            
            # Reemplazar el archivo
            self.image = InMemoryUploadedFile(
                output,
                'ImageField',
                self.image.name,
                f'image/{image_format.lower()}',
                sys.getsizeof(output),
                None
            )
        
        super().save(*args, **kwargs)
    
    def get_file_size_display(self):
        """Retorna el tamaño del archivo en formato legible"""
        if not self.file_size:
            return "N/A"
        
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
