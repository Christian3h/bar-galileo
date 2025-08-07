from django import forms
from .models import Role, UserProfile, RolePermission
from django.contrib.auth.models import User

class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['nombre', 'descripcion']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['user', 'rol']

class RolePermissionForm(forms.ModelForm):
    class Meta:
        model = RolePermission
        fields = ['rol', 'modulo', 'accion']

RolePermissionFormSet = forms.modelformset_factory(
    RolePermission,
    form=RolePermissionForm,
    extra=0,
    can_delete=True
)
