from django.core.management.base import BaseCommand
from tables.models import Pedido, Factura
from decimal import Decimal

class Command(BaseCommand):
    help = 'Crea facturas de prueba con datos limpios'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creando facturas de prueba...'))
        
        # Obtener pedidos que no tienen factura
        pedidos = Pedido.objects.filter(factura__isnull=True)[:5]  # Solo los primeros 5
        
        facturas_creadas = 0
        for pedido in pedidos:
            try:
                total_pedido = pedido.total()
                if total_pedido > 0:
                    factura = Factura.objects.create(
                        pedido=pedido,
                        total=Decimal(str(total_pedido))
                    )
                    facturas_creadas += 1
                    self.stdout.write(f'Factura #{factura.numero} creada - Total: ${total_pedido}')
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creando factura para pedido {pedido.id}: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'Total de facturas creadas: {facturas_creadas}'))
