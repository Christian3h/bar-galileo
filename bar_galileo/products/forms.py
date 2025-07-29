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
            'nombre_categoria': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'contacto', 'telefono', 'direccion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'contacto': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.NumberInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class MarcaForm(forms.ModelForm):
    class Meta:
        model = Marca
        fields = ['marca', 'descripcion']
        widgets = {
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
