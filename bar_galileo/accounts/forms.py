from django import forms
from allauth.account.forms import LoginForm, AddEmailForm
from allauth.account.models import EmailAddress
from captcha.fields import CaptchaField

class CustomLoginForm(LoginForm):
    captcha = CaptchaField(label='Captcha')

    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        self.fields['login'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Usuario'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Contraseña'})

class CustomAddEmailForm(AddEmailForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(CustomAddEmailForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = super().clean_email()
        if self.request and self.request.user.is_authenticated:
            if self.request.user.emailaddress_set.filter(email__iexact=email).exists():
                raise forms.ValidationError("Esta dirección de correo ya está asociada a tu cuenta.")
        return email
