from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('usuarios/', views.user_list, name='user_list'),
    path('panel/', views.panel_usuario, name='panel_usuario'),
]
