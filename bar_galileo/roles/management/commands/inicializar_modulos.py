from django.core.management.base import BaseCommand
from roles.models import Module, Action, Role, RolePermission
from django.conf import settings


class Command(BaseCommand):
    help = 'Inicializa módulos y acciones en el sistema de roles y permisos'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Iniciando configuración de módulos y acciones...'))

        # Crear acciones básicas
        acciones = ['ver', 'crear', 'editar', 'eliminar']
        for accion_nombre in acciones:
            accion, created = Action.objects.get_or_create(nombre=accion_nombre)
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Acción creada: {accion_nombre}'))
            else:
                self.stdout.write(f'  Acción existente: {accion_nombre}')

        # Lista de módulos del proyecto
        modulos = [
            'products',
            'tables',
            'users',
            'roles',
            'expenses',
            'nominas',
            'admin_dashboard',
            'facturacion',
            'notifications',
            'backups',
            'reportes',  # ← Módulo de reportes
            'core',
            'accounts',
        ]

        # Crear módulos
        for modulo_nombre in modulos:
            modulo, created = Module.objects.get_or_create(nombre=modulo_nombre)
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Módulo creado: {modulo_nombre}'))
            else:
                self.stdout.write(f'  Módulo existente: {modulo_nombre}')

        # Crear rol de administrador si no existe
        rol_admin, created = Role.objects.get_or_create(
            nombre='Administrador',
            defaults={'descripcion': 'Acceso completo a todos los módulos'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Rol Administrador creado'))
        else:
            self.stdout.write('  Rol Administrador existente')

        # Asignar todos los permisos al administrador
        self.stdout.write(self.style.WARNING('\nAsignando permisos al Administrador...'))
        permisos_creados = 0
        for modulo in Module.objects.all():
            for accion in Action.objects.all():
                _, created = RolePermission.objects.get_or_create(
                    rol=rol_admin,
                    modulo=modulo,
                    accion=accion
                )
                if created:
                    permisos_creados += 1

        if permisos_creados > 0:
            self.stdout.write(self.style.SUCCESS(f'✓ {permisos_creados} permisos asignados al Administrador'))
        else:
            self.stdout.write('  Todos los permisos ya estaban asignados')

        # Resumen
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('Configuración completada:'))
        self.stdout.write(f'  • Módulos registrados: {Module.objects.count()}')
        self.stdout.write(f'  • Acciones registradas: {Action.objects.count()}')
        self.stdout.write(f'  • Roles creados: {Role.objects.count()}')
        self.stdout.write(f'  • Permisos totales: {RolePermission.objects.count()}')
        self.stdout.write(self.style.SUCCESS('='*50))
