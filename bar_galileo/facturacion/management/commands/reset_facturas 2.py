from django.core.management.base import BaseCommand
from django.db import connection, transaction
from decimal import InvalidOperation

class Command(BaseCommand):
    help = 'Elimina facturas problemáticas que causan errores de decimal'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Eliminando facturas problemáticas...'))
        
        with transaction.atomic():
            with connection.cursor() as cursor:
                # Contar facturas antes
                cursor.execute("SELECT COUNT(*) FROM tables_factura")
                total_before = cursor.fetchone()[0]
                self.stdout.write(f'Facturas antes: {total_before}')
                
                # Eliminar todas las facturas y recrear desde cero
                cursor.execute("DELETE FROM tables_factura")
                
                self.stdout.write(f'Todas las facturas eliminadas.')
                
                # Resetear el contador de autoincremento
                cursor.execute("DELETE FROM sqlite_sequence WHERE name='tables_factura'")
                
        self.stdout.write(self.style.SUCCESS('Facturas problemáticas eliminadas. Ahora puede crear nuevas facturas limpias.'))
