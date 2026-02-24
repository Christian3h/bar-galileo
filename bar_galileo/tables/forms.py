from django import forms
from .models import Mesa

class MesaForm(forms.ModelForm):
    class Meta:
        model = Mesa
        fields = ['nombre', 'descripcion', 'estado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la mesa'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción (opcional)'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'nombre': 'Nombre de la Mesa',
            'descripcion': 'Descripción',
            'estado': 'Estado',
        }
    
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if not nombre or not nombre.strip():
            raise forms.ValidationError('El nombre de la mesa es obligatorio.')
        
        nombre = nombre.strip()
        
        # Validar longitud
        if len(nombre) > 50:
            raise forms.ValidationError('El nombre no puede exceder 50 caracteres.')
        
        # Validar unicidad (case-insensitive)
        if self.instance.pk:
            # Editando una mesa existente
            if Mesa.objects.exclude(pk=self.instance.pk).filter(nombre__iexact=nombre).exists():
                raise forms.ValidationError('Ya existe una mesa con este nombre.')
        else:
            # Creando una nueva mesa
            if Mesa.objects.filter(nombre__iexact=nombre).exists():
                raise forms.ValidationError('Ya existe una mesa con este nombre.')
        
        return nombre
    
    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion')
        if descripcion and len(descripcion) > 200:
            raise forms.ValidationError('La descripción no puede exceder 200 caracteres.')
        return descripcion
    
    def clean_estado(self):
        estado = self.cleaned_data.get('estado')
        if not estado:
            raise forms.ValidationError('El estado es obligatorio.')
        return estado
