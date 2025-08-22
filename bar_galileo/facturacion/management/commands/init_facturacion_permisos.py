from django.core.management.base import BaseCommand
from roles.models import Module, Action

class Command(BaseCommand):
    help = 'Inicializa el módulo y acciones para facturación'

    def handle(self, *args, **options):
        # Crear el módulo de facturación
        modulo, created = Module.objects.get_or_create(
            nombre='facturacion'
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Módulo "facturacion" creado exitosamente.')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Módulo "facturacion" ya existe.')
            )
        
        # Crear las acciones necesarias
        acciones = ['ver', 'eliminar']
        
        for accion_nombre in acciones:
            accion, created = Action.objects.get_or_create(
                nombre=accion_nombre
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Acción "{accion_nombre}" creada exitosamente.')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Acción "{accion_nombre}" ya existe.')
                )
        
        self.stdout.write(
            self.style.SUCCESS('Inicialización de permisos de facturación completada.')
        )
