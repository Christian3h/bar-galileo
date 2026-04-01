"""Suite de pruebas unificada para Bar Galileo.

Incluye pruebas unitarias e integración sobre productos, facturación, usuarios,
gastos, mesas, flujos de pedido/factura, acceso a dashboard, OCR y WebSockets.
"""

import json
from decimal import Decimal
from datetime import timedelta
from unittest.mock import MagicMock, patch

from allauth.socialaccount.models import SocialAccount
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import JsonResponse
from django.test import Client, TestCase, override_settings
from django.urls import path, reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from expenses.forms import ExpenseForm
from expenses.models import ExpenseCategory
from products.models import Categoria, Producto
from rag_chat.document_loader import DocumentLoader
from roles.models import Action, Module, Role, RolePermission, UserProfile
from tables.models import Factura, Mesa, Pedido, PedidoItem


class MockRAGDocumentStore:
	"""Mock simple para simular guardado en BD cuando no existe modelo RAG persistente."""

	rows = []

	@classmethod
	def reset(cls):
		cls.rows = []

	@classmethod
	def create(cls, **kwargs):
		cls.rows.append(kwargs)
		return kwargs


@csrf_exempt
def rag_upload_test_view(request):
	"""Vista de prueba para simular flujo upload -> OCR -> guardado en BD mock."""
	if request.method != "POST":
		return JsonResponse({"error": "method_not_allowed"}, status=405)

	uploaded = request.FILES.get("file")
	if not uploaded:
		return JsonResponse({"error": "file_required"}, status=400)

	loader = DocumentLoader(use_ocr=True)
	pages_data, total_pages = loader.load_pdf("dummy.pdf")
	extracted_text = " ".join(page["text"] for page in pages_data).strip()

	record = MockRAGDocumentStore.create(
		filename=uploaded.name,
		extracted_text=extracted_text,
		page_count=total_pages,
	)

	return JsonResponse({"ok": True, "record": record})


urlpatterns = [
	path("test/rag/upload/", rag_upload_test_view, name="test_rag_upload"),
]


class ProductsUnitTests(TestCase):
	"""Pruebas unitarias de creación y validación de productos."""

	def setUp(self):
		self.categoria = Categoria.objects.create(nombre_categoria="Bebidas")

	def test_crear_producto_valido(self):
		producto = Producto.objects.create(
			nombre="Limonada",
			precio_compra=Decimal("3000.00"),
			precio_venta=Decimal("5000.00"),
			stock=20,
			id_categoria=self.categoria,
		)
		self.assertEqual(producto.nombre, "Limonada")
		self.assertEqual(producto.precio_venta, Decimal("5000.00"))
		self.assertEqual(producto.stock, 20)

	def test_no_permita_producto_con_precio_negativo(self):
		with self.assertRaises(ValidationError):
			Producto.objects.create(
				nombre="Producto invalido",
				precio_compra=Decimal("1000.00"),
				precio_venta=Decimal("-1.00"),
				stock=5,
				id_categoria=self.categoria,
			)


class FacturacionUnitTests(TestCase):
	"""Pruebas unitarias de cálculo de total de factura a partir de items."""

	def setUp(self):
		self.categoria = Categoria.objects.create(nombre_categoria="Cocteles")
		self.producto_1 = Producto.objects.create(
			nombre="Mojito",
			precio_compra=Decimal("8000.00"),
			precio_venta=Decimal("12000.00"),
			stock=30,
			id_categoria=self.categoria,
		)
		self.producto_2 = Producto.objects.create(
			nombre="Piña Colada",
			precio_compra=Decimal("9000.00"),
			precio_venta=Decimal("15000.00"),
			stock=20,
			id_categoria=self.categoria,
		)
		self.mesa = Mesa.objects.create(nombre="Mesa A", estado="disponible")

	def test_calcular_total_factura_desde_items(self):
		pedido = Pedido.objects.create(mesa=self.mesa)
		PedidoItem.objects.create(
			pedido=pedido,
			producto=self.producto_1,
			cantidad=2,
			precio_unitario=Decimal("12000.00"),
		)
		PedidoItem.objects.create(
			pedido=pedido,
			producto=self.producto_2,
			cantidad=1,
			precio_unitario=Decimal("15000.00"),
		)

		total_esperado = Decimal("39000.00")
		self.assertEqual(pedido.total(), total_esperado)

		factura = Factura.objects.create(pedido=pedido, total=pedido.total())
		self.assertEqual(factura.total, total_esperado)


class UsersUnitTests(TestCase):
	"""Pruebas unitarias de seguridad de credenciales de usuario."""

	def test_password_se_hashea_al_crear_usuario(self):
		raw_password = "MiPasswordSegura123"
		user = User.objects.create_user(
			username="usuario_hash",
			email="hash@example.com",
			password=raw_password,
		)
		self.assertNotEqual(user.password, raw_password)
		self.assertTrue(user.check_password(raw_password))


class ExpensesUnitTests(TestCase):
	"""Pruebas unitarias de validación de fechas para gastos."""

	def setUp(self):
		self.user = User.objects.create_user(username="gastos_user", password="123456")
		self.category = ExpenseCategory.objects.create(name="Servicios")

	def test_gasto_con_fecha_futura_dispara_error_validacion(self):
		fixed_now = timezone.datetime(2026, 3, 26, 10, 0, 0, tzinfo=timezone.get_current_timezone())
		future_date = fixed_now.date() + timedelta(days=1)

		form = ExpenseForm()
		form.cleaned_data = {"date": future_date}

		with patch("expenses.forms.timezone.now", return_value=fixed_now):
			with self.assertRaises(ValidationError) as exc:
				form.clean_date()

		self.assertIn("no puede ser futura", str(exc.exception).lower())


class TablesUnitTests(TestCase):
	"""Pruebas unitarias de transición de estado de mesas."""

	def test_cambio_estado_mesa_disponible_ocupada_disponible(self):
		mesa = Mesa.objects.create(nombre="Mesa 12", estado="disponible")

		mesa.estado = "ocupada"
		mesa.save(update_fields=["estado"])
		mesa.refresh_from_db()
		self.assertEqual(mesa.estado, "ocupada")

		mesa.estado = "disponible"
		mesa.save(update_fields=["estado"])
		mesa.refresh_from_db()
		self.assertEqual(mesa.estado, "disponible")


class PedidoStockFacturaIntegrationTests(TestCase):
	"""Pruebas de integración del flujo crear pedido -> actualizar stock -> facturar."""

	def setUp(self):
		self.client = Client()
		self.user = User.objects.create_user(username="mesero", password="abc12345")
		self.client.force_login(self.user)

		categoria = Categoria.objects.create(nombre_categoria="Licores")
		self.producto = Producto.objects.create(
			nombre="Whisky",
			precio_compra=Decimal("20000.00"),
			precio_venta=Decimal("30000.00"),
			stock=10,
			id_categoria=categoria,
		)
		self.mesa = Mesa.objects.create(nombre="Mesa Flujo", estado="ocupada")

	def test_flujo_pedido_actualiza_stock_y_genera_factura(self):
		payload = {
			"mesa_id": self.mesa.id,
			"producto_id": self.producto.id_producto,
			"cantidad": 2,
		}

		with patch("tables.views_api.get_channel_layer", return_value=MagicMock()):
			with patch(
				"tables.views_api.async_to_sync",
				side_effect=lambda _fn: (lambda *args, **kwargs: None),
			):
				with patch("tables.views_api.notificar_usuario"):
					add_resp = self.client.post(
						reverse("tables:api_agregar_item"),
						data=json.dumps(payload),
						content_type="application/json",
					)
					self.assertEqual(add_resp.status_code, 200)

					pedido = Pedido.objects.get(mesa=self.mesa, estado="en_proceso")
					self.assertEqual(pedido.items.count(), 1)
					self.assertEqual(pedido.total(), Decimal("60000.00"))

					fact_resp = self.client.post(
						reverse("tables:api_facturar_pedido", args=[pedido.id]),
						content_type="application/json",
					)
					self.assertEqual(fact_resp.status_code, 200)

		self.producto.refresh_from_db()
		pedido.refresh_from_db()

		self.assertEqual(self.producto.stock, 8)
		self.assertEqual(pedido.estado, "facturado")

		factura = Factura.objects.get(pedido=pedido)
		self.assertEqual(factura.total, Decimal("60000.00"))


class GoogleOAuthDashboardIntegrationTests(TestCase):
	"""Pruebas de integración del flujo login Google OAuth simulado y acceso a dashboard."""

	def setUp(self):
		self.client = Client()
		self.user = User.objects.create_user(
			username="oauth_user",
			email="oauth@example.com",
			password="Segura123",
		)

		self.role = Role.objects.create(nombre="Administrador", descripcion="Rol admin")
		UserProfile.objects.create(user=self.user, rol=self.role)

		modulo = Module.objects.create(nombre="dashboard")
		accion = Action.objects.create(nombre="ver")
		RolePermission.objects.create(rol=self.role, modulo=modulo, accion=accion)

	def test_login_google_simulado_permite_acceso_dashboard(self):
		with patch("allauth.socialaccount.providers.google.provider.GoogleProvider.id", "google"):
			SocialAccount.objects.create(user=self.user, provider="google", uid="google-uid-123")
			self.client.force_login(self.user)

			response = self.client.get("/dashboard/")

		self.assertEqual(response.status_code, 200)


@override_settings(ROOT_URLCONF="core.tests")
class RagUploadOcrIntegrationTests(TestCase):
	"""Pruebas de integración del flujo carga de archivo -> OCR -> guardado en BD mock."""

	def setUp(self):
		self.client = Client()
		MockRAGDocumentStore.reset()

	def test_upload_dispara_ocr_y_guarda_texto_en_store_mock(self):
		fake_file = SimpleUploadedFile(
			"manual.pdf",
			b"%PDF-1.4 test content",
			content_type="application/pdf",
		)

		with patch("core.tests.DocumentLoader.__init__", return_value=None):
			with patch(
				"core.tests.DocumentLoader.load_pdf",
				return_value=([
					{"page": 1, "text": "Texto extraido por OCR", "metadata": {"page_number": 1}},
				], 1),
			):
				with patch("rag_chat.document_loader.pytesseract", create=True) as pytesseract_mock:
					pytesseract_mock.image_to_string.return_value = "Texto OCR"
					response = self.client.post(
						reverse("test_rag_upload"),
						{"file": fake_file},
					)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(MockRAGDocumentStore.rows), 1)
		self.assertIn("Texto extraido por OCR", MockRAGDocumentStore.rows[0]["extracted_text"])


class WebsocketIntegrationTests(TestCase):
	"""Pruebas de integración WebSocket con Django Channels y envío de mensaje."""

	def setUp(self):
		self.user = User.objects.create_user(username="ws_user", password="12345678")

	def test_websocket_notificaciones_recibe_mensaje_tras_conectar(self):
		async def scenario():
			from bar_galileo.asgi import application

			communicator = WebsocketCommunicator(application, "/ws/notificaciones/")
			communicator.scope["user"] = self.user

			connected, _ = await communicator.connect()
			self.assertTrue(connected)

			channel_layer = get_channel_layer()
			await channel_layer.group_send(
				f"user_{self.user.id}",
				{"type": "enviar_mensaje", "message": "hola desde test"},
			)

			payload = await communicator.receive_json_from()
			self.assertEqual(payload["message"], "hola desde test")

			await communicator.disconnect()

		async_to_sync(scenario)()


# Cómo ejecutar:
# 1) Todos los tests de este archivo:
#    python manage.py test core.tests
# 2) Una clase específica:
#    python manage.py test core.tests.PedidoStockFacturaIntegrationTests
