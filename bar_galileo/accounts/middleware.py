from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
from allauth.account.signals import user_logged_in
from django.dispatch import receiver

# Lista para almacenar usuarios que recién iniciaron sesión
recently_logged_in_users = {}

@receiver(user_logged_in)
def mark_user_as_recently_logged_in(sender, request, user, **kwargs):
    """Marca al usuario como recién logueado para la redirección"""
    recently_logged_in_users[user.id] = True

class AdminRedirectMiddleware:
    """
    Middleware para redirigir automáticamente al administrador al dashboard
    únicamente después de iniciar sesión.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Procesar la solicitud solo si el usuario está autenticado
        if request.user.is_authenticated:
            user_id = request.user.id
            # Verificar si el usuario acaba de iniciar sesión y tiene rol de administrador
            if user_id in recently_logged_in_users and hasattr(request.user, 'userprofile') and request.user.userprofile.rol:
                # Identificar si el rol es de administrador
                role_name = request.user.userprofile.rol.nombre.lower()
                
                # Si es administrador, redirigir al dashboard y limpiar el estado
                if 'admin' in role_name or role_name == 'administrador':
                    # Eliminar al usuario de la lista para que no sea redirigido en futuras visitas
                    del recently_logged_in_users[user_id]
                    return redirect(reverse('admin_dashboard:dashboard'))
        
        # Si no se cumple la condición o después de la redirección
        response = self.get_response(request)
        return response