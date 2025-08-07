from django.urls import path
from .views import RolListView, RolCreateView, RolPermisosView

app_name = 'roles'

urlpatterns = [
    path('', RolListView.as_view(), name='rol_list'),
    path('crear/', RolCreateView.as_view(), name='rol_create'),
    path('<int:role_id>/permisos/', RolPermisosView.as_view(), name='rol_permisos'),
]
