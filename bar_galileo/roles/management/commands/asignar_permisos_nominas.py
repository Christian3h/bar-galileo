from django.core.management.base import BaseCommand
from roles.models import Role, Module, Action

class Command(BaseCommand):
    help = 'Agregar permisos de nóminas al rol Administrador'

    def handle(self, *args, **options):
        try:
            # Obtener el rol de administrador
            admin_role = Role.objects.get(nombre='Administrador')
            
            # Obtener el módulo de nóminas
            try:
                nominas_module = Module.objects.get(nombre='nominas')
            except Module.DoesNotExist:
                nominas_module = Module.objects.create(nombre='nominas')
                self.stdout.write(self.style.SUCCESS(f'Módulo de nóminas creado exitosamente'))
            
            # Obtener todas las acciones
            actions = Action.objects.all()
            
            # Asignar todas las acciones del módulo de nóminas al rol administrador
            for action in actions:
                admin_role.permissions.get_or_create(
                    module=nominas_module,
                    action=action
                )
            
            self.stdout.write(self.style.SUCCESS(f'Permisos de nóminas asignados correctamente al rol Administrador'))
        except Role.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'El rol Administrador no existe'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))