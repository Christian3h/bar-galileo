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


def _optimize_image(image_field, max_width, max_height):
    """Abre, redimensiona y comprime una imagen."""
    img = Image.open(image_field)
    width, height = img.size

    if img.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = background

    if img.width > max_width or img.height > max_height:
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        width, height = img.size

    extension = os.path.splitext(image_field.name)[1].lower()
    image_format = 'JPEG'
    if extension == '.png':
        image_format = 'PNG'
    elif extension == '.webp':
        image_format = 'WEBP'

    output = BytesIO()
    if image_format == 'JPEG':
        img.save(output, format='JPEG', quality=85, optimize=True)
    elif image_format == 'PNG':
        img.save(output, format='PNG', optimize=True)
    elif image_format == 'WEBP':
        img.save(output, format='WEBP', quality=85, optimize=True)

    output.seek(0)
    file_size = output.getbuffer().nbytes

    new_file = InMemoryUploadedFile(
        output,
        'ImageField',
        image_field.name,
        f'image/{image_format.lower()}',
        sys.getsizeof(output),
        None
    )
    return new_file, width, height, file_size


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
        if self.image:
            new_file, w, h, size = _optimize_image(self.image, 2000, 2000)
            self.image = new_file
            self.width = w
            self.height = h
            self.file_size = size
        super().save(*args, **kwargs)

    def get_file_size_display(self):
        if not self.file_size:
            return "N/A"
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"


class SiteContent(models.Model):
    """Contenido de texto editable para cada sección de la página de inicio"""

    SECTION_CHOICES = [
        ('hero', 'Sección Hero (Portada)'),
        ('about', 'Sección Acerca de'),
        ('cocktails', 'Sección Cócteles'),
        ('services', 'Sección Servicios'),
        ('reservations', 'Sección Reservas'),
    ]

    section = models.CharField(
        max_length=50,
        choices=SECTION_CHOICES,
        unique=True,
        verbose_name="Sección"
    )

    # Hero
    hero_title = models.CharField(max_length=200, blank=True, verbose_name="Título principal")
    hero_subtitle = models.TextField(blank=True, verbose_name="Subtítulo / Descripción")
    hero_button1_text = models.CharField(max_length=100, blank=True, verbose_name="Texto botón 1")
    hero_button2_text = models.CharField(max_length=100, blank=True, verbose_name="Texto botón 2")

    # About
    about_title = models.CharField(max_length=200, blank=True, verbose_name="Título")
    about_paragraph1 = models.TextField(blank=True, verbose_name="Párrafo 1")
    about_paragraph2 = models.TextField(blank=True, verbose_name="Párrafo 2")
    about_paragraph3 = models.TextField(blank=True, verbose_name="Párrafo 3")

    # Cocktails
    cocktails_title = models.CharField(max_length=200, blank=True, verbose_name="Título")
    cocktails_subtitle = models.TextField(blank=True, verbose_name="Subtítulo")

    # Services
    services_title = models.CharField(max_length=200, blank=True, verbose_name="Título")
    services_subtitle = models.TextField(blank=True, verbose_name="Subtítulo")
    service1_number = models.CharField(max_length=20, blank=True, verbose_name="Estadística 1 (número)")
    service1_title = models.CharField(max_length=100, blank=True, verbose_name="Estadística 1 (título)")
    service1_description = models.TextField(blank=True, verbose_name="Estadística 1 (descripción)")
    service2_number = models.CharField(max_length=20, blank=True, verbose_name="Estadística 2 (número)")
    service2_title = models.CharField(max_length=100, blank=True, verbose_name="Estadística 2 (título)")
    service2_description = models.TextField(blank=True, verbose_name="Estadística 2 (descripción)")
    service3_number = models.CharField(max_length=20, blank=True, verbose_name="Estadística 3 (número)")
    service3_title = models.CharField(max_length=100, blank=True, verbose_name="Estadística 3 (título)")
    service3_description = models.TextField(blank=True, verbose_name="Estadística 3 (descripción)")
    service4_number = models.CharField(max_length=20, blank=True, verbose_name="Estadística 4 (número)")
    service4_title = models.CharField(max_length=100, blank=True, verbose_name="Estadística 4 (título)")
    service4_description = models.TextField(blank=True, verbose_name="Estadística 4 (descripción)")

    # Reservations
    reservations_title = models.CharField(max_length=200, blank=True, verbose_name="Título")
    reservations_text = models.TextField(blank=True, verbose_name="Texto descriptivo")
    reservations_whatsapp = models.CharField(max_length=30, blank=True, verbose_name="Número de WhatsApp")
    reservations_button_text = models.CharField(max_length=100, blank=True, default="Reservar por WhatsApp", verbose_name="Texto del botón")

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Contenido del Sitio"
        verbose_name_plural = "Contenido del Sitio"

    def __str__(self):
        return f"Contenido: {self.get_section_display()}"

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
        if self.image:
            new_file, w, h, size = _optimize_image(self.image, 1920, 1080)
            self.image = new_file
            self.width = w
            self.height = h
            self.file_size = size
        super().save(*args, **kwargs)

    def get_file_size_display(self):
        if not self.file_size:
            return "N/A"
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
