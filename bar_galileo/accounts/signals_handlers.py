
from allauth.account.signals import user_logged_in, user_signed_up, password_reset
from django.dispatch import receiver
from notifications.utils import notificar_usuario
from django.utils.translation import gettext_lazy as _
from django.contrib import messages

@receiver(user_logged_in)
def handle_user_logged_in(sender, request, user, **kwargs):
    print(f"[DEBUG][Signals] Signal user_logged_in received for user: {user.username}")
    """
    Notifica al usuario cuando inicia sesión.
    """
    mensaje = _("¡Bienvenido de nuevo! Has iniciado sesión correctamente.")
    notificar_usuario(user, str(mensaje))

@receiver(user_signed_up)
def handle_user_signed_up(sender, request, user, **kwargs):
    print(f"[DEBUG][Signals] Signal user_signed_up received for user: {user.username}")
    """
    Notifica al usuario cuando se registra.
    """
    mensaje = _("¡Gracias por registrarte! Tu cuenta ha sido creada.")
    notificar_usuario(user, str(mensaje))

@receiver(password_reset)
def handle_password_reset(sender, request, user, **kwargs):
    print(f"[DEBUG][Signals] Signal password_reset received for user: {user.username}")
    """
    Notifica al usuario cuando su contraseña ha sido reseteada.
    """
    mensaje = _("Tu contraseña ha sido cambiada correctamente.")
    notificar_usuario(user, str(mensaje))
