"""
Comando para inicializar los permisos del módulo de reportes.
Este comando crea el módulo 'reportes' y las acciones necesarias en el sistema de roles.
"""

from django.core.management.base import BaseCommand
from reportes.initial_data import crear_modulos_reportes


class Command(BaseCommand):
    help = 'Inicializa los permisos del módulo de reportes'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Inicializando módulo de reportes...'))
        
        try:
            crear_modulos_reportes()
            self.stdout.write(self.style.SUCCESS('✅ Módulo de reportes inicializado correctamente'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error al inicializar el módulo: {str(e)}'))
