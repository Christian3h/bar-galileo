
from allauth.account.signals import user_logged_in, user_signed_up, password_reset
from django.dispatch import receiver
from notifications.utils import notificar_usuario
from django.utils.translation import gettext_lazy as _
from django.contrib import messages

@receiver(user_logged_in)
def handle_user_logged_in(sender, request, user, **kwargs):
    """
    Usa el framework de mensajes de Django para notificar al usuario cuando inicia sesión.
    """
    messages.success(request, _("¡Bienvenido de nuevo! Has iniciado sesión correctamente."))

@receiver(user_signed_up)
def handle_user_signed_up(sender, request, user, **kwargs):
    """
    Notifica al usuario cuando se registra.
    """
    mensaje = _("¡Gracias por registrarte! Tu cuenta ha sido creada.")
    notificar_usuario(user, str(mensaje))

@receiver(password_reset)
def handle_password_reset(sender, request, user, **kwargs):
    """
    Notifica al usuario cuando su contraseña ha sido reseteada.
    """
    mensaje = _("Tu contraseña ha sido cambiada correctamente.")
    notificar_usuario(user, str(mensaje))
