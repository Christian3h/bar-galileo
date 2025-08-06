from django.urls import path
from . import views, views_api

urlpatterns = [
    # Rutas existentes
    path('mesas/', views.lista_mesas, name='mesas_lista'),
    path('mesas/crear/', views.crear_mesa, name='crear_mesa'),
    path('mesas/<int:mesa_id>/editar/', views.editar_mesa, name='editar_mesa'),
    path('mesas/<int:mesa_id>/confirmar-eliminar/', views.confirmar_eliminar_mesa, name='confirmar_eliminar_mesa'),
    path('mesas/<int:mesa_id>/eliminar/', views.eliminar_mesa, name='eliminar_mesa'),
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
