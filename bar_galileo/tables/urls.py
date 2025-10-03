from django.urls import path
from . import views, views_api

app_name = 'tables'

urlpatterns = [
<<<<<<< HEAD
    # Rutas para Mesas con Vistas Basadas en Clases
    path('mesas/', views.MesaListView.as_view(), name='mesas_lista'),
    path('mesas/crear/', views.MesaCreateView.as_view(), name='crear_mesa'),
    path('mesas/<int:pk>/editar/', views.MesaUpdateView.as_view(), name='editar_mesa'),
    path('mesas/<int:pk>/eliminar/', views.MesaDeleteView.as_view(), name='eliminar_mesa'),

    # Rutas que ahora usan Vistas Basadas en Clases
    path('mesas/<int:mesa_id>/confirmar-eliminar/', views.ConfirmarEliminarMesaView.as_view(), name='confirmar_eliminar_mesa'),
    path('mesas/<int:mesa_id>/liberar/', views.LiberarMesaView.as_view(), name='liberar_mesa'),
    path('mesas/<int:mesa_id>/estado/', views.CambiarEstadoMesaView.as_view(), name='actualizar_estado'),
=======
    # Rutas existentes
    path('mesas/', views.lista_mesas, name='mesas_lista'),
    path('mesas/crear/', views.crear_mesa, name='crear_mesa'),
    path('mesas/<int:mesa_id>/editar/', views.editar_mesa, name='editar_mesa'),
    path('mesas/<int:mesa_id>/confirmar-eliminar/', views.confirmar_eliminar_mesa, name='confirmar_eliminar_mesa'),
    path('mesas/<int:mesa_id>/eliminar/', views.eliminar_mesa, name='eliminar_mesa'),
    path('mesas/<int:mesa_id>/liberar/', views.liberar_mesa, name='liberar_mesa'),
    path('mesas/<int:mesa_id>/estado/', views.cambiar_estado, name='actualizar_estado'),
>>>>>>> f550aac13c0202e2f4652738b7d329dd256a899a
    
    # Rutas API para pedidos
    path('api/mesas/<int:mesa_id>/pedido/', views_api.mesa_pedido_api, name='api_mesa_pedido'),
    path('api/pedidos/agregar-item/', views_api.agregar_item_api, name='api_agregar_item'),
<<<<<<< HEAD
    path('api/pedidos/actualizar-item/<int:item_id>/', views_api.actualizar_item_api, name='api_actualizar_item'),
    path('api/pedidos/eliminar-item/<int:item_id>/', views_api.eliminar_item_api, name='api_eliminar_item'),
    path('api/pedidos/<int:pedido_id>/facturar/', views_api.facturar_pedido_api, name='api_facturar_pedido'),
    path('api/pedidos/<int:pedido_id>/usuarios/', views_api.pedido_manage_user_api, name='api_pedido_manage_user'),
    path('api/users/', views_api.get_all_users_api, name='api_get_all_users'),
    
    # Ruta para ver la factura
    path('facturas/<int:factura_id>/', views.VerFacturaView.as_view(), name='ver_factura'),
=======
    path('api/pedidos/eliminar-item/<int:item_id>/', views_api.eliminar_item_api, name='api_eliminar_item'),
    path('api/pedidos/<int:pedido_id>/facturar/', views_api.facturar_pedido_api, name='api_facturar_pedido'),
    
    # Ruta para ver la factura
    path('facturas/<int:factura_id>/', views.ver_factura, name='ver_factura'),
>>>>>>> f550aac13c0202e2f4652738b7d329dd256a899a
]
