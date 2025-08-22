from users.models import Emergencia

Emergencia.objects.all().update(
    nombre='',
    relacion='',
    telefono='',
    telefono_alt='',
    sangre='',
    alergias=''
)
print('Todos los contactos de emergencia han sido borrados (campos vacíos).')
