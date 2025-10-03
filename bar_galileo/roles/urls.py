from django.urls import path
<<<<<<< HEAD
from .views import RolListView, RolCreateView, RolPermisosView, RolUpdateView, RolDeleteView
=======
from .views import RolListView, RolCreateView, RolPermisosView
>>>>>>> f550aac13c0202e2f4652738b7d329dd256a899a

app_name = 'roles'

urlpatterns = [
    path('', RolListView.as_view(), name='rol_list'),
    path('crear/', RolCreateView.as_view(), name='rol_create'),
<<<<<<< HEAD
    path('<int:pk>/editar/', RolUpdateView.as_view(), name='rol_update'),
    path('<int:pk>/eliminar/', RolDeleteView.as_view(), name='rol_delete'),
    path('<int:role_id>/permisos/', RolPermisosView.as_view(), name='rol_permisos'),
]
=======
    path('<int:role_id>/permisos/', RolPermisosView.as_view(), name='rol_permisos'),
]
>>>>>>> f550aac13c0202e2f4652738b7d329dd256a899a
