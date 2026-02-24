from django.urls import path
from .views import RolListView, RolCreateView, RolPermisosView, RolUpdateView, RolDeleteView

app_name = 'roles'

urlpatterns = [
    path('', RolListView.as_view(), name='rol_list'),
    path('crear/', RolCreateView.as_view(), name='rol_create'),
    path('<int:pk>/editar/', RolUpdateView.as_view(), name='rol_update'),
    path('<int:pk>/eliminar/', RolDeleteView.as_view(), name='rol_delete'),
    path('<int:role_id>/permisos/', RolPermisosView.as_view(), name='rol_permisos'),
]