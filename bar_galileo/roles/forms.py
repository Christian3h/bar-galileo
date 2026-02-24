from django import forms
from django.core.exceptions import ValidationError
from .models import Role, UserProfile, RolePermission
from django.contrib.auth.models import User

class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del rol'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción del rol'}),
        }
        labels = {
            'nombre': 'Nombre del Rol',
            'descripcion': 'Descripción',
        }
    
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if not nombre or not nombre.strip():
            raise forms.ValidationError('El nombre del rol es obligatorio.')
        
        nombre = nombre.strip()
        
        # Validar longitud
        if len(nombre) > 100:
            raise forms.ValidationError('El nombre no puede exceder 100 caracteres.')
        
        # Validar unicidad (case-insensitive)
        if self.instance.pk:
            # Editando un rol existente
            if Role.objects.exclude(pk=self.instance.pk).filter(nombre__iexact=nombre).exists():
                raise forms.ValidationError('Ya existe un rol con este nombre.')
        else:
            # Creando un nuevo rol
            if Role.objects.filter(nombre__iexact=nombre).exists():
                raise forms.ValidationError('Ya existe un rol con este nombre.')
        
        return nombre
    
    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion')
        if descripcion and len(descripcion) > 500:
            raise forms.ValidationError('La descripción no puede exceder 500 caracteres.')
        return descripcion

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['user', 'rol']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'rol': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'user': 'Usuario',
            'rol': 'Rol',
        }
    
    def clean_user(self):
        user = self.cleaned_data.get('user')
        if not user:
            raise forms.ValidationError('El usuario es obligatorio.')
        return user
    
    def clean_rol(self):
        rol = self.cleaned_data.get('rol')
        if not rol:
            raise forms.ValidationError('El rol es obligatorio.')
        return rol

class RolePermissionForm(forms.ModelForm):
    class Meta:
        model = RolePermission
        fields = ['rol', 'modulo', 'accion']
        widgets = {
            'rol': forms.Select(attrs={'class': 'form-control'}),
            'modulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del módulo'}),
            'accion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Acción permitida'}),
        }
        labels = {
            'rol': 'Rol',
            'modulo': 'Módulo',
            'accion': 'Acción',
        }
    
    def clean_rol(self):
        rol = self.cleaned_data.get('rol')
        if not rol:
            raise forms.ValidationError('El rol es obligatorio.')
        return rol
    
    def clean_modulo(self):
        modulo = self.cleaned_data.get('modulo')
        if not modulo or not modulo.strip():
            raise forms.ValidationError('El módulo es obligatorio.')
        return modulo.strip()
    
    def clean_accion(self):
        accion = self.cleaned_data.get('accion')
        if not accion or not accion.strip():
            raise forms.ValidationError('La acción es obligatoria.')
        return accion.strip()

RolePermissionFormSet = forms.modelformset_factory(
    RolePermission,
    form=RolePermissionForm,
    extra=0,
    can_delete=True
)
