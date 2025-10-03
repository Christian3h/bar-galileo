
from allauth.account.signals import user_logged_in, user_signed_up, password_reset
from django.dispatch import receiver
from notifications.utils import notificar_usuario
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
<<<<<<< HEAD
from users.models import PerfilUsuario
import requests
from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO
=======
>>>>>>> f550aac13c0202e2f4652738b7d329dd256a899a

@receiver(user_logged_in)
def handle_user_logged_in(sender, request, user, **kwargs):
    print(f"[DEBUG][Signals] Signal user_logged_in received for user: {user.username}")
<<<<<<< HEAD
    mensaje = _("¡Bienvenido de nuevo! Has iniciado sesión correctamente.")
    notificar_usuario(user, str(mensaje))

    sociallogin = kwargs.get('sociallogin')
    if not sociallogin:
        print("[DEBUG][Signals] No social login detected.")
        return

    if sociallogin.account.provider == 'google':
        print(f"[DEBUG][Signals] Social login via Google for user: {user.username}")
        try:
            perfil, created = PerfilUsuario.objects.get_or_create(user=user)
            
            if not perfil.nombre:
                perfil.nombre = sociallogin.account.extra_data.get('name', user.get_full_name())
                perfil.save()

            if perfil.avatar:
                print(f"[DEBUG][Signals] User {user.username} already has an avatar. Skipping.")
                return

            picture_url = sociallogin.account.extra_data.get('picture')
            if not picture_url:
                print(f"[DEBUG][Signals] No picture URL found in extra_data for {user.username}.")
                return
            
            print(f"[DEBUG][Signals] Found picture URL: {picture_url}")
            try:
                response = requests.get(picture_url, stream=True)
                response.raise_for_status()
                
                img = Image.open(response.raw)
                
                buffer = BytesIO()
                img.save(buffer, format='WEBP', quality=85)
                buffer.seek(0)

                file_name = f"{user.id}_avatar.webp"
                perfil.avatar.save(file_name, ContentFile(buffer.read()), save=True)
                print(f"[DEBUG][Signals] Successfully saved Google avatar as WebP for {user.username}")

            except requests.exceptions.RequestException as e:
                print(f"[DEBUG][Signals] Error downloading Google avatar for {user.username}: {e}")
            except Exception as e:
                print(f"[DEBUG][Signals] Error processing image for {user.username}: {e}")
        
        except Exception as e:
            print(f"[DEBUG][Signals] An unexpected error occurred in avatar logic for user {user.username}: {e}")

@receiver(user_signed_up)
def handle_user_signed_up(sender, request, user, **kwargs):
    print(f"[DEBUG][Signals] Signal user_signed_up received for user: {user.username}")
    perfil, created = PerfilUsuario.objects.get_or_create(user=user)
    
    if created:
        sociallogin = kwargs.get('sociallogin')
        if sociallogin:
            if sociallogin.account.provider == 'google':
                perfil.nombre = sociallogin.account.extra_data.get('name', user.get_full_name())
        else:
            perfil.nombre = user.get_full_name() or user.username
        
        perfil.save()
        print(f"[DEBUG][Signals] Populated PerfilUsuario for new user {user.username}")

=======
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
>>>>>>> f550aac13c0202e2f4652738b7d329dd256a899a
    mensaje = _("¡Gracias por registrarte! Tu cuenta ha sido creada.")
    notificar_usuario(user, str(mensaje))

@receiver(password_reset)
def handle_password_reset(sender, request, user, **kwargs):
    print(f"[DEBUG][Signals] Signal password_reset received for user: {user.username}")
<<<<<<< HEAD
=======
    """
    Notifica al usuario cuando su contraseña ha sido reseteada.
    """
>>>>>>> f550aac13c0202e2f4652738b7d329dd256a899a
    mensaje = _("Tu contraseña ha sido cambiada correctamente.")
    notificar_usuario(user, str(mensaje))
