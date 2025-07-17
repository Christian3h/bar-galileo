from django.urls import path
from . import views

urlpatterns = [
    path('mesas/', views.lista_mesas, name='lista_mesas'),
    path('mesas/crear/', views.crear_mesa, name='crear_mesa'),
    path('mesas/eliminar/<int:mesa_id>/', views.eliminar_mesa, name='eliminar_mesa'),
    path('mesas/estado/<int:mesa_id>/', views.cambiar_estado, name='cambiar_estado'),
    path('mesas/actualizar_estado/<int:mesa_id>/', views.cambiar_estado, name='actualizar_estado'),
    path('mesas/editar/<int:mesa_id>/', views.editar_mesa, name='editar_mesa'),


]
