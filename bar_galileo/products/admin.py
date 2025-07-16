from django.contrib import admin
from .models import Producto

from .models import (
    Categoria, Marca, Proveedor, Producto,
    Cliente, Empleado, Mesas, TipoPago, Pedido,
    DetallePedido, Facturacion, DescuentosPedido,
    Compra, Stock, Nomina, MovimientosFinancieros,
    Reportes, ReporteFacturas, ReporteCompras,
    ReporteGastos, ReporteNomina, ReporteStock,
)

for modelo in [
    Categoria, Marca, Proveedor, Producto,
    Cliente, Empleado, Mesas, TipoPago, Pedido,
    DetallePedido, Facturacion, DescuentosPedido,
    Compra, Stock, Nomina, MovimientosFinancieros,
    Reportes, ReporteFacturas, ReporteCompras,
    ReporteGastos, ReporteNomina, ReporteStock,
]:
    admin.site.register(modelo)