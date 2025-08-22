from django.core.management.base import BaseCommand
from roles.models import Module, Action, Role, RolePermission
from facturacion.initial_data import FACTURACION_PERMISOS

class Command(BaseCommand):
    help = 'Inicializa los permisos del módulo de facturación'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando configuración de permisos de facturación...'))
        
        # Crear el módulo de facturación si no existe
        modulo_facturacion, created = Module.objects.get_or_create(nombre='facturacion')
        if created:
            self.stdout.write(self.style.SUCCESS(f'Módulo "facturacion" creado exitosamente.'))
        else:
            self.stdout.write(f'Módulo "facturacion" ya existe.')

        # Crear las acciones necesarias
        acciones_necesarias = ['ver', 'eliminar']
        for accion_nombre in acciones_necesarias:
            accion, created = Action.objects.get_or_create(nombre=accion_nombre)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Acción "{accion_nombre}" creada exitosamente.'))
            else:
                self.stdout.write(f'Acción "{accion_nombre}" ya existe.')

        # Asignar permisos al rol de administrador si existe
        try:
            rol_admin = Role.objects.get(nombre__icontains='admin')
            modulo_facturacion = Module.objects.get(nombre='facturacion')
            
            for accion_nombre in acciones_necesarias:
                accion = Action.objects.get(nombre=accion_nombre)
                permiso, created = RolePermission.objects.get_or_create(
                    rol=rol_admin,
                    modulo=modulo_facturacion,
                    accion=accion
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(
                        f'Permiso "{accion_nombre}" en módulo "facturacion" asignado a rol "{rol_admin.nombre}".'
                    ))
                else:
                    self.stdout.write(
                        f'Permiso "{accion_nombre}" en módulo "facturacion" ya existe para rol "{rol_admin.nombre}".'
                    )
                    
        except Role.DoesNotExist:
            self.stdout.write(self.style.WARNING('No se encontró un rol de administrador. Los permisos deben asignarse manualmente.'))

        self.stdout.write(self.style.SUCCESS('Configuración de permisos de facturación completada.'))
