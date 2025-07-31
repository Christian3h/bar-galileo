from django import forms
from .models import Mesa

class MesaForm(forms.ModelForm):
    class Meta:
        model = Mesa
        fields = ['nombre', 'descripcion', 'estado',]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            
        }
