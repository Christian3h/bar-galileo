"""
Formulario para la gestión de productos en el sistema Bar Galileo.
Utiliza el modelo Producto y permite crear y editar productos desde el frontend.
"""

from django import forms
import re
from .models import Producto, Categoria, Proveedor, Marca


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'precio_compra', 'precio_venta', 'stock', 'descripcion', 'id_categoria', 'id_proveedor', 'id_marca', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del producto', 'required': True}),
            'precio_compra': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Precio de compra', 'required': True, 'step': '0.01', 'min': '0.01'}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Precio de venta', 'required': True, 'step': '0.01', 'min': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cantidad en stock', 'required': True, 'min': '0'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción del producto (opcional)'}),
            'id_categoria': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'id_proveedor': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'id_marca': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'nombre': 'Nombre del Producto',
            'precio_compra': 'Precio de Compra',
            'precio_venta': 'Precio de Venta',
            'stock': 'Stock Inicial',
            'descripcion': 'Descripción',
            'id_categoria': 'Categoría',
            'id_proveedor': 'Proveedor',
            'id_marca': 'Marca',
            'activo': 'Producto Activo',
        }
    
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if not nombre or not nombre.strip():
            raise forms.ValidationError('El nombre del producto es obligatorio.')
        return nombre.strip()
    
    def clean_precio_compra(self):
        precio_compra = self.cleaned_data.get('precio_compra')
        if precio_compra is None:
            raise forms.ValidationError('El precio de compra es obligatorio.')
        if precio_compra <= 0:
            raise forms.ValidationError('El precio de compra debe ser mayor que cero.')
        return precio_compra
    
    def clean_precio_venta(self):
        precio_venta = self.cleaned_data.get('precio_venta')
        if precio_venta is None:
            raise forms.ValidationError('El precio de venta es obligatorio.')
        if precio_venta <= 0:
            raise forms.ValidationError('El precio de venta debe ser mayor que cero.')
        return precio_venta
    
    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock is None or stock == '':
            raise forms.ValidationError('El stock es obligatorio.')
        try:
            stock = int(stock)
        except (ValueError, TypeError):
            raise forms.ValidationError('El stock debe ser un número válido.')
        if stock <= 0:
            raise forms.ValidationError('El stock debe ser mayor a 0.')
        return stock
    
    def clean_id_categoria(self):
        categoria = self.cleaned_data.get('id_categoria')
        if not categoria:
            raise forms.ValidationError('La categoría es obligatoria.')
        return categoria
    
    def clean_id_proveedor(self):
        proveedor = self.cleaned_data.get('id_proveedor')
        if not proveedor:
            raise forms.ValidationError('El proveedor es obligatorio.')
        return proveedor
    
    def clean_id_marca(self):
        marca = self.cleaned_data.get('id_marca')
        if not marca:
            raise forms.ValidationError('La marca es obligatoria.')
        return marca
    
    def clean(self):
        cleaned_data = super().clean()
        precio_compra = cleaned_data.get('precio_compra')
        precio_venta = cleaned_data.get('precio_venta')
        
        # Validar que el precio de venta sea mayor que el de compra
        if precio_compra and precio_venta:
            if precio_venta <= precio_compra:
                raise forms.ValidationError({
                    'precio_venta': 'El precio de venta debe ser mayor que el precio de compra.'
                })
        
        return cleaned_data

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

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            # Convert BigIntegerField to string for regex validation
            telefono_str = str(telefono)
            # Colombian phone number regex: starts with 3, 10 digits long
            colombian_phone_regex = r'^3\d{9}$'
            if not re.match(colombian_phone_regex, telefono_str):
                raise forms.ValidationError('El número de teléfono debe ser colombiano (10 dígitos, empieza con 3).')
        return telefono

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