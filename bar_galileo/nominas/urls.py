from django.urls import path
from .views import (
    EmpleadoListView, EmpleadoCreateView, EmpleadoUpdateView, EmpleadoDeleteView,
    EmpleadoDetailView, PagoCreateView, PagoListView, BonificacionCreateView,
    agregar_pago, agregar_bonificacion, buscar_usuarios_disponibles
)

app_name = "nominas"

urlpatterns = [
    # Rutas de empleados
    path("", EmpleadoListView.as_view(), name="empleado_list"),
    path("crear/", EmpleadoCreateView.as_view(), name="empleado_crear"),
    path("editar/<int:pk>/", EmpleadoUpdateView.as_view(), name="empleado_editar"),
    path("eliminar/<int:pk>/", EmpleadoDeleteView.as_view(), name="empleado_eliminar"),
    path("empleado/<int:pk>/", EmpleadoDetailView.as_view(), name="empleado_detail"),

    # API para buscar usuarios
    path("api/buscar-usuarios/", buscar_usuarios_disponibles, name="buscar_usuarios"),

    # Rutas de pagos
    path("pagos/", PagoListView.as_view(), name="pago_list"),
    path("pagos/crear/", PagoCreateView.as_view(), name="pago_crear"),
    path("empleado/<int:empleado_id>/agregar-pago/", agregar_pago, name="agregar_pago"),

    # Rutas de bonificaciones
    path("bonificaciones/crear/", BonificacionCreateView.as_view(), name="bonificacion_crear"),
    path("empleado/<int:empleado_id>/agregar-bonificacion/", agregar_bonificacion, name="agregar_bonificacion"),
]
