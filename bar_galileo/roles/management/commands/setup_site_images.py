from django.core.management.base import BaseCommand
from roles.models import Role, Module, Action, RolePermission

class Command(BaseCommand):
    help = 'Crear módulo site_images y asignar permisos al rol Administrador'

    def handle(self, *args, **options):
        try:
            modulo, created = Module.objects.get_or_create(nombre='site_images')
            if created:
                self.stdout.write(self.style.SUCCESS('Módulo site_images creado'))
            else:
                self.stdout.write('Módulo site_images ya existía')

            admin_role = Role.objects.filter(nombre__icontains='admin').first()
            if not admin_role:
                self.stdout.write(self.style.ERROR('No se encontró rol admin'))
                return

            actions = Action.objects.all()
            for action in actions:
                _, c = RolePermission.objects.get_or_create(
                    rol=admin_role,
                    modulo=modulo,
                    accion=action
                )
                estado = 'CREADO' if c else 'ya existía'
                self.stdout.write(f'  Permiso {action.nombre}: {estado}')

            self.stdout.write(self.style.SUCCESS(f'Permisos de site_images asignados al rol {admin_role.nombre}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
