from django import forms
from django.utils.html import strip_tags
from .models import SiteImage, CarouselImage, SiteImageSection
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from core.security.validators import ProductSSTIValidator, DescriptionSSTIValidator, GenericSSTIValidator


class SiteImageSectionForm(forms.ModelForm):
    """Formulario para crear/editar secciones de imágenes"""
    class Meta:
        model = SiteImageSection
        fields = ['name', 'section_type', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la sección',
                'data-validate': 'product'
            }),
            'section_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción de la sección (opcional)',
                'rows': 3,
                'data-validate': 'description'
            }),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            # Usar validador SSTI
            validator = ProductSSTIValidator()
            validator(name)
        return name

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if description:
            # Usar validador SSTI
            validator = DescriptionSSTIValidator()
            validator(description)
        return description


class SiteImageForm(forms.ModelForm):
    """Formulario para subir imágenes del sitio"""
    class Meta:
        model = SiteImage
        fields = ['section', 'title', 'image', 'alt_text', 'order', 'is_active']
        widgets = {
            'section': forms.Select(attrs={
                'class': 'form-control'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título de la imagen',
                'data-validate': 'any'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/jpg,image/png,image/webp'
            }),
            'alt_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Texto alternativo para accesibilidad',
                'data-validate': 'any'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'value': 0
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')

        if image and isinstance(image, UploadedFile):
            max_size = 5 * 1024 * 1024  # 5MB
            if image.size > max_size:
                raise ValidationError(
                    f'El tamaño del archivo no debe exceder 5MB. '
                    f'Tamaño actual: {image.size / (1024 * 1024):.2f}MB'
                )

            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
            if image.content_type not in allowed_types:
                raise ValidationError(
                    'Formato de imagen no válido. Formatos permitidos: JPG, JPEG, PNG, WebP'
                )

        return image

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title:
            # Usar validador SSTI
            validator = GenericSSTIValidator()
            validator(title)
        return title

    def clean_alt_text(self):
        alt_text = self.cleaned_data.get('alt_text')
        if alt_text:
            # Usar validador SSTI
            validator = GenericSSTIValidator()
            validator(alt_text)
        return alt_text


class CarouselImageForm(forms.ModelForm):
    """Formulario para subir imágenes del carrusel"""
    class Meta:
        model = CarouselImage
        fields = ['title', 'image', 'alt_text', 'caption', 'link_url', 'order', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título de la imagen',
                'data-validate': 'any'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/jpg,image/png,image/webp'
            }),
            'alt_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Texto alternativo para accesibilidad',
                'data-validate': 'any'
            }),
            'caption': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Texto descriptivo (opcional)',
                'data-validate': 'any'
            }),
            'link_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'URL de enlace (opcional)'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'value': 0
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')

        if image and isinstance(image, UploadedFile):
            max_size = 10 * 1024 * 1024  # 10MB para carrusel
            if image.size > max_size:
                raise ValidationError(
                    f'El tamaño del archivo no debe exceder 10MB. '
                    f'Tamaño actual: {image.size / (1024 * 1024):.2f}MB'
                )

            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
            if image.content_type not in allowed_types:
                raise ValidationError(
                    'Formato de imagen no válido. Formatos permitidos: JPG, JPEG, PNG, WebP'
                )

        return image

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title:
            # Usar validador SSTI
            validator = GenericSSTIValidator()
            validator(title)
        return title

    def clean_alt_text(self):
        alt_text = self.cleaned_data.get('alt_text')
        if alt_text:
            # Usar validador SSTI
            validator = GenericSSTIValidator()
            validator(alt_text)
        return alt_text

    def clean_caption(self):
        caption = self.cleaned_data.get('caption')
        if caption:
            # Usar validador SSTI
            validator = GenericSSTIValidator()
            validator(caption)
        return caption


class BulkCarouselReorderForm(forms.Form):
    """Formulario para reordenar múltiples imágenes del carrusel"""
    image_orders = forms.CharField(
        widget=forms.HiddenInput(),
        help_text='JSON con el nuevo orden de las imágenes'
    )


class SiteContentForm(forms.ModelForm):
    """Formulario para editar el contenido de texto de cada sección de la home"""

    class Meta:
        from .models import SiteContent
        model = SiteContent
        exclude = ['section', 'updated_at']
        widgets = {
            'hero_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: BAR GALILEO'}),
            'hero_subtitle': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'hero_button1_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: EXPLORAR CARTA'}),
            'hero_button2_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: NUESTRA HISTORIA'}),
            'about_title': forms.TextInput(attrs={'class': 'form-control'}),
            'about_paragraph1': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'about_paragraph2': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'about_paragraph3': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'cocktails_title': forms.TextInput(attrs={'class': 'form-control'}),
            'cocktails_subtitle': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'services_title': forms.TextInput(attrs={'class': 'form-control'}),
            'services_subtitle': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'service1_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 5+'}),
            'service1_title': forms.TextInput(attrs={'class': 'form-control'}),
            'service1_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'service2_number': forms.TextInput(attrs={'class': 'form-control'}),
            'service2_title': forms.TextInput(attrs={'class': 'form-control'}),
            'service2_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'service3_number': forms.TextInput(attrs={'class': 'form-control'}),
            'service3_title': forms.TextInput(attrs={'class': 'form-control'}),
            'service3_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'service4_number': forms.TextInput(attrs={'class': 'form-control'}),
            'service4_title': forms.TextInput(attrs={'class': 'form-control'}),
            'service4_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'reservations_title': forms.TextInput(attrs={'class': 'form-control'}),
            'reservations_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'reservations_whatsapp': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 573044029343'}),
            'reservations_button_text': forms.TextInput(attrs={'class': 'form-control'}),
        }
