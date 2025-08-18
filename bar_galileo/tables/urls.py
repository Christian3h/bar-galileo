from django.urls import path
from . import views, views_api

app_name = 'tables'

urlpatterns = [
    # Rutas para Mesas con Vistas Basadas en Clases
    path('mesas/', views.MesaListView.as_view(), name='mesas_lista'),
    path('mesas/crear/', views.MesaCreateView.as_view(), name='crear_mesa'),
    path('mesas/<int:pk>/editar/', views.MesaUpdateView.as_view(), name='editar_mesa'),
    path('mesas/<int:pk>/eliminar/', views.MesaDeleteView.as_view(), name='eliminar_mesa'),

    # Rutas que aún usan vistas basadas en funciones (si las hay)
    path('mesas/<int:mesa_id>/confirmar-eliminar/', views.confirmar_eliminar_mesa, name='confirmar_eliminar_mesa'),
    path('mesas/<int:mesa_id>/liberar/', views.liberar_mesa, name='liberar_mesa'),
    path('mesas/<int:mesa_id>/estado/', views.cambiar_estado, name='actualizar_estado'),
    
    # Rutas API para pedidos
    path('api/mesas/<int:mesa_id>/pedido/', views_api.mesa_pedido_api, name='api_mesa_pedido'),
    path('api/pedidos/agregar-item/', views_api.agregar_item_api, name='api_agregar_item'),
    path('api/pedidos/eliminar-item/<int:item_id>/', views_api.eliminar_item_api, name='api_eliminar_item'),
    path('api/pedidos/<int:pedido_id>/facturar/', views_api.facturar_pedido_api, name='api_facturar_pedido'),
    
    # Ruta para ver la factura
    path('facturas/<int:factura_id>/', views.ver_factura, name='ver_factura'),
]
