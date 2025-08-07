from django.core.management.base import BaseCommand
from products.models import Producto, Stock


class Command(BaseCommand):
    help = 'Sincroniza el stock del campo producto con la tabla Stock'

    def handle(self, *args, **options):
        productos = Producto.objects.all()
        sincronizados = 0
        
        for producto in productos:
            # Verificar si ya existe un registro de stock para este producto
            stock_existente = Stock.objects.filter(id_producto=producto).exists()
            
            if not stock_existente and producto.stock is not None:
                # Crear un registro inicial en la tabla Stock
                Stock.objects.create(
                    id_producto=producto,
                    cantidad=producto.stock
                )
                sincronizados += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Sincronizado stock para {producto.nombre}: {producto.stock}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Sincronización completada. {sincronizados} productos sincronizados.'
            )
        )
