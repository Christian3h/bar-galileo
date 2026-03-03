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
                'placeholder': 'Nombre del reporte',
                'required': True
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'periodo': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'formato': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descripción del reporte (opcional)'
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
    
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if not nombre or not nombre.strip():
            raise forms.ValidationError('El nombre del reporte es obligatorio.')
        return nombre.strip()
    
    def clean_tipo(self):
        tipo = self.cleaned_data.get('tipo')
        if not tipo:
            raise forms.ValidationError('El tipo de reporte es obligatorio.')
        return tipo
    
    def clean_periodo(self):
        periodo = self.cleaned_data.get('periodo')
        if not periodo:
            raise forms.ValidationError('El periodo es obligatorio.')
        return periodo
    
    def clean_formato(self):
        formato = self.cleaned_data.get('formato')
        if not formato:
            raise forms.ValidationError('El formato es obligatorio.')
        return formato
    
    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')
        if archivo:
            # Validar tamaño (máximo 10MB para reportes)
            if archivo.size > 10 * 1024 * 1024:
                raise forms.ValidationError('El archivo no puede superar 10MB.')
            
            # Validar tipo de archivo
            allowed_types = ['application/pdf', 'application/vnd.ms-excel', 
                           'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                           'text/csv']
            if archivo.content_type not in allowed_types:
                raise forms.ValidationError('Solo se permiten archivos PDF, Excel o CSV.')
        return archivo
    
    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        
        if fecha_inicio and fecha_fin:
            if fecha_fin < fecha_inicio:
                raise forms.ValidationError({
                    'fecha_fin': 'La fecha de fin debe ser posterior a la fecha de inicio.'
                })
            
            # Validar rango máximo (2 años)
            diff = fecha_fin - fecha_inicio
            if diff.days > 730:
                raise forms.ValidationError(
                    'El rango de fechas no puede ser mayor a 2 años.'
                )
        
        return cleaned_data


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
        queryset=User.objects.filter(
            reportes_creados__isnull=False
        ).distinct().order_by('username'),
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
