from django import forms
from django.utils import timezone
from django.utils.html import strip_tags
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.urls import reverse
from roles.models import Role
from .models import Empleado, Pago, Bonificacion
from core.security.validators import NameSSTIValidator, EmailSSTIValidator, PhoneSSTIValidator, GenericSSTIValidator, DescriptionSSTIValidator

class DateInput(forms.DateInput):
    input_type = 'date'

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('format', '%Y-%m-%d')
        super().__init__(*args, **kwargs)

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
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo', 'required': True, 'data-validate': 'name'}),
            'salario': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Salario base', 'required': True}),
            'fecha_contratacion': DateInput(attrs={'class': 'form-control', 'required': True}),
            'estado': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'tipo_contrato': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com', 'required': True, 'data-validate': 'email'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+123456789', 'required': True, 'data-validate': 'phone'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Dirección completa', 'required': True, 'data-validate': 'any'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        hoy = timezone.localdate().isoformat()
        self.fields['fecha_contratacion'].widget.attrs['max'] = hoy

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

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if not nombre or not nombre.strip():
            raise forms.ValidationError('El nombre del empleado es obligatorio.')
        nombre = nombre.strip()
        # Usar validador SSTI
        validator = NameSSTIValidator()
        validator(nombre)
        return nombre
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email or not email.strip():
            raise forms.ValidationError('El email es obligatorio.')
        email = email.strip()
        # Usar validador SSTI
        validator = EmailSSTIValidator()
        validator(email)
        return email
    
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if not telefono or not telefono.strip():
            raise forms.ValidationError('El teléfono es obligatorio.')
        telefono = telefono.strip()
        # Usar validador SSTI
        validator = PhoneSSTIValidator()
        validator(telefono)
        return telefono
    
    def clean_direccion(self):
        direccion = self.cleaned_data.get('direccion')
        if not direccion or not direccion.strip():
            raise forms.ValidationError('La dirección es obligatoria.')
        direccion = direccion.strip()
        # Usar validador SSTI
        validator = GenericSSTIValidator()
        validator(direccion)
        return direccion

    def clean_salario(self):
        salario = self.cleaned_data.get('salario')
        if salario is None:
            raise forms.ValidationError('El salario es obligatorio.')
        if salario <= 0:
            raise forms.ValidationError("El salario debe ser mayor que cero.")
        if salario > 100000000:  # Límite razonable
            raise forms.ValidationError("El salario no puede superar $100,000,000.")
        return salario
    
    def clean_fecha_contratacion(self):
        fecha_contratacion = self.cleaned_data.get('fecha_contratacion')
        if not fecha_contratacion:
            raise forms.ValidationError('La fecha de contratación es obligatoria.')
        if fecha_contratacion > timezone.now().date():
            raise forms.ValidationError('La fecha de contratación no puede ser futura.')
        return fecha_contratacion

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
            'comprobante': forms.FileInput(attrs={'class': 'form-control', 'accept': '.jpg,.jpeg,.png,.pdf'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        hoy = timezone.localdate().isoformat()
        self.fields['fecha_pago'].widget.attrs['max'] = hoy

    def clean_monto(self):
        monto = self.cleaned_data.get('monto')
        if monto is None:
            raise forms.ValidationError("El monto es obligatorio.")
        if monto <= 0:
            raise forms.ValidationError("El monto del pago debe ser mayor que cero.")
        if monto > 100000000:  # Límite razonable
            raise forms.ValidationError("El monto no puede superar $100,000,000.")
        return monto
    
    def clean_fecha_pago(self):
        fecha_pago = self.cleaned_data.get('fecha_pago')
        if not fecha_pago:
            raise forms.ValidationError("La fecha de pago es obligatoria.")
        if fecha_pago > timezone.now().date():
            raise forms.ValidationError("La fecha de pago no puede ser futura.")
        return fecha_pago
    
    def clean_empleado(self):
        empleado = self.cleaned_data.get('empleado')
        if not empleado:
            raise forms.ValidationError("Debe seleccionar un empleado.")
        if empleado.estado != 'activo':
            raise forms.ValidationError("No se pueden registrar pagos para empleados inactivos.")
        return empleado
    
    def clean_comprobante(self):
        import os
        comprobante = self.cleaned_data.get('comprobante')
        if comprobante:
            # Validar tamaño (máximo 5MB)
            if comprobante.size > 5 * 1024 * 1024:
                raise forms.ValidationError('El archivo no puede superar 5MB.')

            # Validar extensión del archivo
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.pdf']
            ext = os.path.splitext(comprobante.name)[1].lower()
            if ext not in allowed_extensions:
                raise forms.ValidationError(
                    f'Formato no permitido ({ext or "sin extensión"}). '
                    'Solo se aceptan imágenes JPG/PNG o archivos PDF.'
                )

            # Validar content_type como segunda capa de seguridad
            allowed_types = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf']
            if comprobante.content_type not in allowed_types:
                raise forms.ValidationError(
                    'El tipo de archivo no está permitido. '
                    'Solo se aceptan imágenes JPG/PNG o archivos PDF.'
                )
        return comprobante

class BonificacionForm(forms.ModelForm):
    class Meta:
        model = Bonificacion
        fields = ["empleado", "nombre", "monto", "recurrente", "fecha_inicio", "fecha_fin"]
        widgets = {
            'empleado': forms.Select(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la bonificación', 'data-validate': 'any'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control'}),
            'recurrente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'fecha_inicio': DateInput(attrs={'class': 'form-control'}),
            'fecha_fin': DateInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        hoy = timezone.localdate().isoformat()
        self.fields['fecha_inicio'].widget.attrs['max'] = hoy
        self.fields['fecha_fin'].widget.attrs['max'] = hoy

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if not nombre or not nombre.strip():
            raise forms.ValidationError('El nombre de la bonificación es obligatorio.')
        nombre = nombre.strip()
        # Usar validador SSTI
        validator = GenericSSTIValidator()
        validator(nombre)
        return nombre
    
    def clean_monto(self):
        monto = self.cleaned_data.get('monto')
        if monto is None:
            raise forms.ValidationError('El monto es obligatorio.')
        if monto <= 0:
            raise forms.ValidationError('El monto debe ser mayor que cero.')
        if monto > 50000000:  # Límite razonable
            raise forms.ValidationError('El monto no puede superar $50,000,000.')
        return monto
    
    def clean_empleado(self):
        empleado = self.cleaned_data.get('empleado')
        if not empleado:
            raise forms.ValidationError('Debe seleccionar un empleado.')
        return empleado
    
    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        empleado = cleaned_data.get('empleado')
        hoy = timezone.localdate()
        
        # Validar que no sean fechas futuras
        if fecha_inicio and fecha_inicio > hoy:
            raise ValidationError({
                'fecha_inicio': 'La fecha de inicio no puede ser una fecha futura.'
            })
        if fecha_fin and fecha_fin > hoy:
            raise ValidationError({
                'fecha_fin': 'La fecha de fin no puede ser una fecha futura.'
            })
        
        # Validar que fecha_fin sea posterior a fecha_inicio
        if fecha_inicio and fecha_fin:
            if fecha_fin < fecha_inicio:
                raise ValidationError({
                    'fecha_fin': 'La fecha de fin debe ser posterior a la fecha de inicio.'
                })
        
        # Validar que fecha_inicio no sea anterior a la contratación
        if fecha_inicio and empleado:
            if fecha_inicio < empleado.fecha_contratacion:
                raise ValidationError({
                    'fecha_inicio': 'La fecha de inicio no puede ser anterior a la fecha de contratación del empleado.'
                })
        
        return cleaned_data

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
