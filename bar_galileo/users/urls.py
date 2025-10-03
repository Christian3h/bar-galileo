from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('usuarios/', views.user_list, name='user_list'),
    path('panel/', views.panel_usuario, name='panel_usuario'),
<<<<<<< HEAD
    path('panel/editar-info/', views.editar_info, name='editar_info'),
    path('panel/borrar-info/', views.borrar_info, name='borrar_info'),
    path('panel/editar-emergencia/', views.editar_emergencia, name='editar_emergencia'),
    path('panel/borrar-emergencia/', views.borrar_emergencia, name='borrar_emergencia'),
    path('api/usuarios/', views.user_list_api, name='api_user_list'),
=======
>>>>>>> f550aac13c0202e2f4652738b7d329dd256a899a
]
