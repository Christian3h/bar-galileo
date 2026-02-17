from django import forms
from .models import SiteImage, CarouselImage, SiteImageSection
from django.core.exceptions import ValidationError


class SiteImageSectionForm(forms.ModelForm):
    """Formulario para crear/editar secciones de imágenes"""
    class Meta:
        model = SiteImageSection
        fields = ['name', 'section_type', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la sección'
            }),
            'section_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción de la sección (opcional)',
                'rows': 3
            }),
        }


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
                'placeholder': 'Título de la imagen'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/jpg,image/png,image/webp'
            }),
            'alt_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Texto alternativo para accesibilidad'
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
        
        if image:
            # Validar tamaño del archivo (máximo 5MB)
            max_size = 5 * 1024 * 1024  # 5MB en bytes
            if image.size > max_size:
                raise ValidationError(
                    f'El tamaño del archivo no debe exceder 5MB. '
                    f'Tamaño actual: {image.size / (1024 * 1024):.2f}MB'
                )
            
            # Validar tipo de contenido
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
            if image.content_type not in allowed_types:
                raise ValidationError(
                    f'Formato de imagen no válido. '
                    f'Formatos permitidos: JPG, JPEG, PNG, WebP'
                )
        
        return image


class CarouselImageForm(forms.ModelForm):
    """Formulario para subir imágenes del carrusel"""
    class Meta:
        model = CarouselImage
        fields = ['title', 'image', 'alt_text', 'caption', 'link_url', 'order', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título de la imagen'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/jpg,image/png,image/webp'
            }),
            'alt_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Texto alternativo para accesibilidad'
            }),
            'caption': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Texto descriptivo (opcional)'
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
        
        if image:
            # Validar tamaño del archivo (máximo 10MB para carrusel)
            max_size = 10 * 1024 * 1024  # 10MB en bytes
            if image.size > max_size:
                raise ValidationError(
                    f'El tamaño del archivo no debe exceder 10MB. '
                    f'Tamaño actual: {image.size / (1024 * 1024):.2f}MB'
                )
            
            # Validar tipo de contenido
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
            if image.content_type not in allowed_types:
                raise ValidationError(
                    f'Formato de imagen no válido. '
                    f'Formatos permitidos: JPG, JPEG, PNG, WebP'
                )
        
        return image


class BulkCarouselReorderForm(forms.Form):
    """Formulario para reordenar múltiples imágenes del carrusel"""
    image_orders = forms.CharField(
        widget=forms.HiddenInput(),
        help_text='JSON con el nuevo orden de las imágenes'
    )
