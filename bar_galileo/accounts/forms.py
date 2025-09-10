from django import forms
from allauth.account.forms import LoginForm
from captcha.fields import CaptchaField

class CustomLoginForm(LoginForm):
    captcha = CaptchaField(label='Captcha')

    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        self.fields['login'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Usuario'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Contraseña'})