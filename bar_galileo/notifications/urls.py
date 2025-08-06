from django.urls import path
from .views import NotificacionesPendientesView

urlpatterns = [
    path("api/notificaciones/pendientes/", NotificacionesPendientesView.as_view(), name="notificaciones_pendientes"),
]
