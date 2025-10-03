from django.core.management.base import BaseCommand
from django.db import connection, transaction
from decimal import Decimal, InvalidOperation
from tables.models import Factura, Pedido

class Command(BaseCommand):
    help = 'Limpia y corrige todas las facturas con datos problemáticos'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando limpieza completa de facturas...'))
        
        with transaction.atomic():
            # Primero, eliminar facturas con valores problemáticos usando SQL directo
            with connection.cursor() as cursor:
                # Verificar facturas existentes
                cursor.execute("SELECT COUNT(*) FROM tables_factura")
                total_original = cursor.fetchone()[0]
                self.stdout.write(f'Total de facturas antes de limpieza: {total_original}')
                
                # Eliminar facturas con totales problemáticos
                cursor.execute("""
                    DELETE FROM tables_factura 
                    WHERE total IS NULL 
                    OR total = '' 
                    OR total = 'None'
                    OR CAST(total AS TEXT) LIKE '%e%'
                    OR CAST(total AS TEXT) LIKE '%.%'
                """)
                
                deleted_count = cursor.rowcount
                self.stdout.write(f'Facturas eliminadas: {deleted_count}')
                
                # Verificar facturas restantes
                cursor.execute("SELECT COUNT(*) FROM tables_factura")
                remaining_count = cursor.fetchone()[0]
                self.stdout.write(f'Facturas restantes: {remaining_count}')
        
        # Ahora recrear facturas válidas para pedidos sin factura
        self.stdout.write('Recreando facturas para pedidos facturados sin factura válida...')
        
        pedidos_facturados = Pedido.objects.filter(estado='facturado')
        pedidos_sin_factura = []
        
        for pedido in pedidos_facturados:
            try:
                # Intentar acceder a la factura
                factura = pedido.factura
                # Intentar acceder al total (esto fallará si hay problemas)
                total = factura.total
                if total is None:
                    pedidos_sin_factura.append(pedido)
            except (Factura.DoesNotExist, InvalidOperation, ValueError):
                pedidos_sin_factura.append(pedido)
        
        self.stdout.write(f'Pedidos facturados sin factura válida: {len(pedidos_sin_factura)}')
        
        # Crear facturas válidas
        facturas_creadas = 0
        for pedido in pedidos_sin_factura:
            try:
                # Calcular el total del pedido
                total_pedido = pedido.total()
                
                if total_pedido > 0:
                    # Crear nueva factura
                    factura = Factura.objects.create(
                        pedido=pedido,
                        total=Decimal(str(total_pedido))
                    )
                    facturas_creadas += 1
                    self.stdout.write(f'Factura #{factura.numero} creada para pedido {pedido.id} - Total: ${total_pedido}')
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creando factura para pedido {pedido.id}: {e}')
                )
        
        self.stdout.write(self.style.SUCCESS(f'Facturas nuevas creadas: {facturas_creadas}'))
        
        # Verificar estado final
        total_facturas_final = Factura.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Total de facturas después de limpieza: {total_facturas_final}'))
        
        self.stdout.write(self.style.SUCCESS('Limpieza de facturas completada exitosamente.'))
