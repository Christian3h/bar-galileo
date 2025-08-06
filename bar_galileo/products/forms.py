"""
Formulario para la gestión de productos en el sistema Bar Galileo.
Utiliza el modelo Producto y permite crear y editar productos desde el frontend.
"""

from django import forms
from .models import Producto, Categoria, Proveedor, Marca


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'precio_compra', 'precio_venta', 'stock', 'descripcion', 'id_categoria', 'id_proveedor', 'id_marca']
        widgets = {campo: forms.TextInput(attrs={'class': 'form-control'}) for campo in ['nombre']}

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre_categoria', 'descripcion']
        widgets = {
            'nombre_categoria': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def clean_nombre_categoria(self):
        nombre = self.cleaned_data.get('nombre_categoria')
        if not nombre or not nombre.strip():
            raise forms.ValidationError('El nombre de la categoría es obligatorio.')
        return nombre.strip()

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'contacto', 'telefono', 'direccion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del proveedor', 'required': True}),
            'contacto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Persona de contacto/Email', 'required': True}),
            'telefono': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Dirección completa', 'required': True}),
        }
        labels = {
            'nombre': 'Proveedor',
            'contacto': 'Email/Contacto',
            'telefono': 'Teléfono',
            'direccion': 'Dirección',
        }
    
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if not nombre or not nombre.strip():
            raise forms.ValidationError('El nombre del proveedor es obligatorio.')
        return nombre.strip()
    
    def clean_contacto(self):
        contacto = self.cleaned_data.get('contacto')
        if not contacto or not contacto.strip():
            raise forms.ValidationError('El contacto es obligatorio.')
        return contacto.strip()
    
    def clean_direccion(self):
        direccion = self.cleaned_data.get('direccion')
        if not direccion or not direccion.strip():
            raise forms.ValidationError('La dirección es obligatoria.')
        return direccion.strip()

class MarcaForm(forms.ModelForm):
    class Meta:
        model = Marca
        fields = ['marca', 'descripcion']
        widgets = {
            'marca': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def clean_marca(self):
        marca = self.cleaned_data.get('marca')
        if not marca or not marca.strip():
            raise forms.ValidationError('El nombre de la marca es obligatorio.')
        return marca.strip()
