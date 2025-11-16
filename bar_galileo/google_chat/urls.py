from django.urls import path
from . import views

app_name = 'google_chat'

urlpatterns = [
    # Crear nueva sesión
    path('api/create/', views.CreateSessionView.as_view(), name='create_session'),

    # Enviar mensaje (con contexto)
    path('api/send/', views.SendMessageView.as_view(), name='send_message'),

    # Obtener historial de una sesión
    path('api/history/<int:session_id>/', views.GetHistoryView.as_view(), name='get_history'),

    # Listar todas las sesiones del usuario
    path('api/sessions/', views.ListSessionsView.as_view(), name='list_sessions'),

    # Eliminar sesión
    path('api/clear/<int:session_id>/', views.ClearSessionView.as_view(), name='clear_session'),
]
