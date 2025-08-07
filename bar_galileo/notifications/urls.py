from django.urls import path
from .views import NotificacionHistoryView, MarkAsReadView, NotificacionesPendientesView

app_name = 'notifications'

urlpatterns = [
    path("api/notifications/history/", NotificacionHistoryView.as_view(), name="notification_history"),
    path("api/notifications/mark-as-read/", MarkAsReadView.as_view(), name="notification_mark_as_read"),
    path("api/notificaciones/pendientes/", NotificacionesPendientesView.as_view(), name="notificaciones_pendientes"),
]
