from django.urls import path
from . import views

app_name = 'roles'

urlpatterns = [
    path('roles/', views.rol_list, name='rol_list'),
    path('roles/crear/', views.rol_create, name='rol_create'),
    path('roles/<int:role_id>/permisos/', views.rol_permisos, name='rol_permisos'),
]
