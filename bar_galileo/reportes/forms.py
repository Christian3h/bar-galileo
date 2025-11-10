from django import forms
from django.contrib.auth.models import User
from .models import Reporte


class ReporteForm(forms.ModelForm):
    """Formulario para crear y editar reportes"""
    
    class Meta:
        model = Reporte
        fields = ['nombre', 'tipo', 'periodo', 'formato', 'descripcion', 'fecha_inicio', 'fecha_fin', 'archivo']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del reporte'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-control'
            }),
            'periodo': forms.Select(attrs={
                'class': 'form-control'
            }),
            'formato': forms.Select(attrs={
                'class': 'form-control'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descripción del reporte'
            }),
            'fecha_inicio': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'fecha_fin': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'archivo': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'nombre': 'Nombre del Reporte',
            'tipo': 'Tipo de Reporte',
            'periodo': 'Periodo',
            'formato': 'Formato de Exportación',
            'descripcion': 'Descripción',
            'fecha_inicio': 'Fecha de Inicio',
            'fecha_fin': 'Fecha de Fin',
            'archivo': 'Archivo del Reporte'
        }


class ReporteFilterForm(forms.Form):
    """Formulario para filtrar reportes"""
    
    tipo = forms.ChoiceField(
        choices=[('', 'Todos los tipos')] + list(Reporte.TIPO_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    periodo = forms.ChoiceField(
        choices=[('', 'Todos los periodos')] + list(Reporte.PERIODO_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    usuario = forms.ModelChoiceField(
        queryset=User.objects.all().order_by('username'),
        required=False,
        empty_label='Todos los usuarios',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    busqueda = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre o descripción...'
        })
    )
