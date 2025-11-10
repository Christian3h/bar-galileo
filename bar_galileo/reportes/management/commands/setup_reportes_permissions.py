from django.core.management.base import BaseCommand
from roles.models import Module, Action, Role, RolePermission
from django.contrib.auth.models import User
from users.models import UserProfile

class Command(BaseCommand):
    help = 'Configurar permisos para el módulo de reportes'

    def handle(self, *args, **options):
        # Crear módulos y acciones
        reportes_module, created = Module.objects.get_or_create(nombre='reportes')
        if created:
            self.stdout.write(f'Módulo "reportes" creado')
        else:
            self.stdout.write(f'Módulo "reportes" ya existe')
        
        ver_action, _ = Action.objects.get_or_create(nombre='ver')
        crear_action, _ = Action.objects.get_or_create(nombre='crear')
        editar_action, _ = Action.objects.get_or_create(nombre='editar')
        eliminar_action, _ = Action.objects.get_or_create(nombre='eliminar')
        
        # Buscar el rol de administrador o crear uno
        admin_role, created = Role.objects.get_or_create(nombre='Administrador')
        if created:
            self.stdout.write(f'Rol "Administrador" creado')
        
        # Asignar todos los permisos de reportes al rol administrador
        perms = [
            (reportes_module, ver_action),
            (reportes_module, crear_action),
            (reportes_module, editar_action),
            (reportes_module, eliminar_action),
        ]
        
        for modulo, accion in perms:
            perm, created = RolePermission.objects.get_or_create(
                rol=admin_role,
                modulo=modulo,
                accion=accion
            )
            if created:
                self.stdout.write(f'Permiso creado: {modulo.nombre} - {accion.nombre}')
        
        # Asignar el rol a los superusuarios que no tengan rol
        superusers = User.objects.filter(is_superuser=True)
        for user in superusers:
            profile, created = UserProfile.objects.get_or_create(user=user)
            if not profile.rol:
                profile.rol = admin_role
                profile.save()
                self.stdout.write(f'Rol asignado al usuario: {user.username}')
        
        self.stdout.write(self.style.SUCCESS('Configuración de permisos completada'))
