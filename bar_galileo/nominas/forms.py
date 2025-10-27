from django import forms
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Empleado, Pago, Bonificacion

class DateInput(forms.DateInput):
    input_type = 'date'

class EmpleadoForm(forms.ModelForm):
    usuario = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        empty_label="Seleccionar usuario (opcional)",
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Conectar este empleado con un usuario del sistema"
    )
    
    class Meta:
        model = Empleado
        fields = [
            "usuario", "nombre", "cargo", "salario", "fecha_contratacion", 
            "estado", "tipo_contrato", "email", "telefono", "direccion"
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo'}),
            'cargo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cargo en la empresa'}),
            'salario': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Salario base'}),
            'fecha_contratacion': DateInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'tipo_contrato': forms.Select(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+123456789'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Dirección completa'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mostrar solo usuarios que no están ya asignados a un empleado
        usuarios_sin_empleado = User.objects.filter(empleado_nomina__isnull=True)
        if self.instance and self.instance.pk and self.instance.usuario:
            # Incluir el usuario actual del empleado en la lista
            usuarios_sin_empleado = usuarios_sin_empleado | User.objects.filter(pk=self.instance.usuario.pk)
        self.fields['usuario'].queryset = usuarios_sin_empleado
        
        # Si hay un usuario seleccionado, prellenar campos
        if self.instance and self.instance.usuario:
            usuario = self.instance.usuario
            if not self.instance.nombre and usuario.first_name:
                self.initial['nombre'] = f"{usuario.first_name} {usuario.last_name}"
            if not self.instance.email and usuario.email:
                self.initial['email'] = usuario.email
    
    def clean_salario(self):
        salario = self.cleaned_data.get('salario')
        if salario and salario <= 0:
            raise forms.ValidationError("El salario debe ser mayor que cero.")
        return salario
    
    def save(self, commit=True):
        empleado = super().save(commit=False)
        
        # Sincronizar datos con el usuario si está seleccionado
        if empleado.usuario:
            empleado.sincronizar_con_usuario()
        
        if commit:
            empleado.save()
        return empleado

class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ["empleado", "fecha_pago", "monto", "tipo", "descripcion", "comprobante"]
        widgets = {
            'empleado': forms.Select(attrs={'class': 'form-control'}),
            'fecha_pago': DateInput(attrs={'class': 'form-control'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'comprobante': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_monto(self):
        monto = self.cleaned_data.get('monto')
        if monto and monto <= 0:
            raise forms.ValidationError("El monto del pago debe ser mayor que cero.")
        return monto

class BonificacionForm(forms.ModelForm):
    class Meta:
        model = Bonificacion
        fields = ["empleado", "nombre", "monto", "recurrente", "fecha_inicio", "fecha_fin"]
        widgets = {
            'empleado': forms.Select(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la bonificación'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control'}),
            'recurrente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'fecha_inicio': DateInput(attrs={'class': 'form-control'}),
            'fecha_fin': DateInput(attrs={'class': 'form-control'}),
        }

class EmpleadoFilterForm(forms.Form):
    estado = forms.ChoiceField(
        choices=[('', 'Todos')] + Empleado.ESTADO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    tipo_contrato = forms.ChoiceField(
        choices=[('', 'Todos')] + Empleado.TIPO_CONTRATO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    busqueda = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Buscar por nombre o cargo'})
    )
