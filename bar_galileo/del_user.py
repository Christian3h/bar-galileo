from django.contrib.auth.models import User
try:
    u = User.objects.get(id=14)
    nombre = u.username
    email = u.email
    u.delete()
    print(f'ELIMINADO: {nombre} / {email}')
except User.DoesNotExist:
    print('YA NO EXISTE')
