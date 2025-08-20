from django.test import TestCase
from django.contrib.auth.models import User
from tables.models import Mesa, Pedido, Factura
from .models import FacturacionManager

class FacturacionManagerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test')
        self.mesa = Mesa.objects.create(nombre='Mesa 1')
        self.pedido = Pedido.objects.create(mesa=self.mesa)
        self.factura = Factura.objects.create(pedido=self.pedido, total=100.00)

    def test_obtener_estadisticas(self):
        estadisticas = FacturacionManager.obtener_estadisticas()
        self.assertEqual(estadisticas['total_facturas'], 1)
        self.assertEqual(estadisticas['total_ingresos'], 100.00)

    def test_filtrar_facturas(self):
        facturas = FacturacionManager.obtener_facturas_con_filtros(busqueda='Mesa 1')
        self.assertEqual(facturas.count(), 1)
