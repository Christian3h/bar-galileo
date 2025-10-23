"""
Script para asignar permisos del módulo de reportes al rol de administrador.
"""

from django.core.management.base import BaseCommand
from roles.models import Module, Action, Role, RolePermission


class Command(BaseCommand):
    help = 'Asigna permisos del módulo de reportes al rol de administrador'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Asignando permisos de reportes al rol admin...'))
        
        try:
            # Obtener el módulo de reportes
            modulo_reportes = Module.objects.get(nombre='reportes')
            
            # Obtener el rol de admin
            try:
                rol_admin = Role.objects.get(nombre='admin')
            except Role.DoesNotExist:
                self.stdout.write(self.style.WARNING('⚠️  Rol "admin" no encontrado. Creando...'))
                rol_admin = Role.objects.create(
                    nombre='admin',
                    descripcion='Rol de administrador con todos los permisos'
                )
            
            # Obtener todas las acciones
            acciones = Action.objects.filter(nombre__in=['ver', 'crear', 'editar', 'eliminar', 'exportar', 'generar'])
            
            # Asignar permisos
            permisos_creados = 0
            for accion in acciones:
                permiso, created = RolePermission.objects.get_or_create(
                    rol=rol_admin,
                    modulo=modulo_reportes,
                    accion=accion
                )
                if created:
                    permisos_creados += 1
                    self.stdout.write(f'   ✓ Permiso creado: {rol_admin.nombre} | {modulo_reportes.nombre} | {accion.nombre}')
            
            if permisos_creados > 0:
                self.stdout.write(self.style.SUCCESS(f'✅ {permisos_creados} permisos asignados correctamente'))
            else:
                self.stdout.write(self.style.SUCCESS('✅ Todos los permisos ya estaban asignados'))
                
        except Module.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ Módulo "reportes" no encontrado. Ejecuta primero: python manage.py inicializar_reportes'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {str(e)}'))
