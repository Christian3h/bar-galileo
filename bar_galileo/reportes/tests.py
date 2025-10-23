from django.test import TestCase
from django.contrib.auth.models import User
from .models import Reporte
from datetime import date


class ReporteModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        
    def test_crear_reporte(self):
        reporte = Reporte.objects.create(
            nombre='Reporte de Prueba',
            tipo='ventas',
            creado_por=self.user,
            fecha_inicio=date.today(),
            fecha_fin=date.today()
        )
        self.assertEqual(reporte.nombre, 'Reporte de Prueba')
        self.assertEqual(reporte.tipo, 'ventas')
