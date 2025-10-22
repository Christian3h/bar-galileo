from django.core.management.base import BaseCommand
from django.db import connection
from decimal import Decimal

class Command(BaseCommand):
    help = 'Corrige facturas con datos problemáticos'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando corrección de facturas...'))
        
        # Usar SQL directo para identificar y corregir facturas problemáticas
        with connection.cursor() as cursor:
            # Primero, veamos qué datos hay en la tabla
            cursor.execute("SELECT id, numero, total FROM tables_factura LIMIT 5")
            rows = cursor.fetchall()
            
            self.stdout.write("Primeras 5 facturas en la base de datos:")
            for row in rows:
                self.stdout.write(f"ID: {row[0]}, Número: {row[1]}, Total: {row[2]}")
            
            # Eliminar facturas con totales problemáticos
            cursor.execute("DELETE FROM tables_factura WHERE total IS NULL OR total = '' OR total = 'None'")
            deleted_count = cursor.rowcount
            
            if deleted_count > 0:
                self.stdout.write(self.style.SUCCESS(f'Se eliminaron {deleted_count} facturas problemáticas.'))
            
            # Verificar cuántas facturas quedan
            cursor.execute("SELECT COUNT(*) FROM tables_factura")
            remaining_count = cursor.fetchone()[0]
            self.stdout.write(f'Facturas restantes: {remaining_count}')
        
        self.stdout.write(self.style.SUCCESS('Corrección de facturas completada.'))
