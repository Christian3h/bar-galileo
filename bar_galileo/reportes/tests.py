from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
from .models import Reporte
from roles.models import Role, Module, Action, RolePermission, UserProfile


class ReporteModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        # Crear rol y permisos necesarios para acceder a las vistas de reportes
        role = Role.objects.create(nombre='rol_test')
        module = Module.objects.create(nombre='reportes')
        action_ver, _ = Action.objects.get_or_create(nombre='ver')
        # Asociar permiso al rol
        RolePermission.objects.create(rol=role, modulo=module, accion=action_ver)
        # Asociar perfil de usuario con el rol
        UserProfile.objects.create(user=self.user, rol=role)
    
    def test_reporte_creation(self):
        """Prueba la creación de un reporte"""
        reporte = Reporte.objects.create(
            nombre='Reporte de prueba',
            tipo='ventas',
            periodo='mensual',
            formato='pdf',
            descripcion='Descripción de prueba',
            creado_por=self.user,
            fecha_inicio=date.today() - timedelta(days=30),
            fecha_fin=date.today()
        )
        
        self.assertEqual(reporte.nombre, 'Reporte de prueba')
        self.assertEqual(reporte.tipo, 'ventas')
        self.assertEqual(str(reporte), 'Reporte de prueba - Ventas')
    
    def test_duracion_dias(self):
        """Prueba el cálculo de duración en días"""
        reporte = Reporte.objects.create(
            nombre='Reporte de prueba',
            tipo='ventas',
            creado_por=self.user,
            fecha_inicio=date.today() - timedelta(days=7),
            fecha_fin=date.today()
        )
        
        self.assertEqual(reporte.duracion_dias, 8)  # 7 días + 1


class ReporteViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.reporte = Reporte.objects.create(
            nombre='Reporte de prueba',
            tipo='ventas',
            creado_por=self.user,
            fecha_inicio=date.today() - timedelta(days=30),
            fecha_fin=date.today()
        )
    
    def test_reporte_list_view(self):
        """Prueba la vista de lista de reportes"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('reportes:reporte_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Reporte de prueba')
    
    def test_reporte_detail_view(self):
        """Prueba la vista de detalle de reporte"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('reportes:reporte_detail', args=[self.reporte.pk])
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.reporte.nombre)
