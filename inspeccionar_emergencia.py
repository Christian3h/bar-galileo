from users.models import PerfilUsuario, Emergencia
from django.contrib.auth.models import User

# Cambia 'tu_usuario' por el username real
user = User.objects.get(username='tu_usuario')
perfil = PerfilUsuario.objects.get(user=user)
emergencia = Emergencia.objects.get(perfil=perfil)
print('Emergencia:', emergencia.nombre, emergencia.relacion, emergencia.telefono, emergencia.telefono_alt, emergencia.sangre, emergencia.alergias)
