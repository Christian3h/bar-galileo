from django import forms
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.urls import reverse
from roles.models import Role
from .models import Empleado, Pago, Bonificacion

class DateInput(forms.DateInput):
    input_type = 'date'

class EmpleadoForm(forms.ModelForm):
    # Campos para gestión de usuario
    USUARIO_CHOICES = [
        ('sin_usuario', 'Sin usuario del sistema'),
        ('usuario_existente', 'Seleccionar usuario existente'),
        ('usuario_nuevo', 'Crear nuevo usuario'),
    ]

    opcion_usuario = forms.ChoiceField(
        choices=USUARIO_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label="Gestión de usuario del sistema",
        initial='sin_usuario',
        required=False
    )

    # Campo de búsqueda de usuario en lugar de select
    buscar_usuario = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Escribe el nombre de usuario o email...',
            'autocomplete': 'off',
            'data-url': '/nominas/api/buscar-usuarios/'
        }),
        label="Buscar usuario",
        help_text="Escribe para buscar usuarios disponibles"
    )

    usuario_existente = forms.ModelChoiceField(
        queryset=User.objects.filter(empleado__isnull=True),
        required=False,
        widget=forms.HiddenInput(),  # Campo oculto, se llenará con JavaScript
        label="Usuario seleccionado"
    )

    # Campo de rol en lugar de cargo texto libre
    rol_cargo = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Rol/Cargo",
        help_text="Selecciona el rol que define el cargo del empleado"
    )

    # Campos para crear nuevo usuario
    username = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'nombre.usuario'}),
        label="Nombre de usuario",
        help_text="Requerido. 150 caracteres o menos. Letras, dígitos y @/./+/-/_ solamente."
    )

    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}),
        label="Contraseña",
        help_text="Mínimo 8 caracteres"
    )

    password_confirm = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar contraseña'}),
        label="Confirmar contraseña"
    )

    email_usuario = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
        label="Email del usuario",
        help_text="Se usará el mismo email del empleado si se deja vacío"
    )

    class Meta:
        model = Empleado
        fields = [
            "nombre", "salario", "fecha_contratacion",
            "estado", "tipo_contrato", "email", "telefono", "direccion"
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo'}),
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

        # Si estamos editando un empleado existente
        if self.instance and self.instance.pk:
            # Pre-llenar el rol si existe
            if hasattr(self.instance, 'user') and self.instance.user and hasattr(self.instance.user, 'userprofile'):
                self.fields['rol_cargo'].initial = self.instance.user.userprofile.rol

            if self.instance.user:
                # Si ya tiene usuario, mostrarlo y no permitir cambiar
                self.fields['opcion_usuario'].initial = 'usuario_existente'
                self.fields['opcion_usuario'].widget = forms.HiddenInput()
                # Agregar el usuario actual al queryset
                self.fields['usuario_existente'].queryset = User.objects.filter(
                    Q(empleado__isnull=True) | Q(id=self.instance.user.id)
                )
                self.fields['usuario_existente'].initial = self.instance.user
                self.fields['buscar_usuario'].widget = forms.HiddenInput()
                self.fields['buscar_usuario'].initial = f"{self.instance.user.username} - {self.instance.user.email}"
            else:
                # Si no tiene usuario, actualizar queryset para excluir usuarios ya asignados
                self.fields['usuario_existente'].queryset = User.objects.filter(empleado__isnull=True)

    def clean_salario(self):
        salario = self.cleaned_data.get('salario')
        if salario and salario <= 0:
            raise forms.ValidationError("El salario debe ser mayor que cero.")
        return salario

    def clean(self):
        cleaned_data = super().clean()
        opcion = cleaned_data.get('opcion_usuario')

        # Solo validar si estamos creando un nuevo empleado o si está cambiando la opción
        if not self.instance.pk or (self.instance.pk and not self.instance.user):

            if opcion == 'usuario_existente':
                if not cleaned_data.get('usuario_existente'):
                    raise ValidationError({
                        'usuario_existente': 'Debe seleccionar un usuario existente'
                    })

            elif opcion == 'usuario_nuevo':
                # Validar campos de nuevo usuario
                username = cleaned_data.get('username')
                password = cleaned_data.get('password')
                password_confirm = cleaned_data.get('password_confirm')

                if not username:
                    raise ValidationError({
                        'username': 'El nombre de usuario es requerido'
                    })

                # Validar que el username no exista
                if User.objects.filter(username=username).exists():
                    raise ValidationError({
                        'username': 'Este nombre de usuario ya existe'
                    })

                if not password:
                    raise ValidationError({
                        'password': 'La contraseña es requerida'
                    })

                if len(password) < 8:
                    raise ValidationError({
                        'password': 'La contraseña debe tener al menos 8 caracteres'
                    })

                if password != password_confirm:
                    raise ValidationError({
                        'password_confirm': 'Las contraseñas no coinciden'
                    })

        return cleaned_data

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
