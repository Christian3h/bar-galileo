from django.urls import path
from . import views

app_name = 'facturacion'

urlpatterns = [
    path('', views.lista_facturas, name='lista_facturas'),
    path('detalle/<int:factura_id>/', views.detalle_factura, name='detalle_factura'),
    path('eliminar/<int:factura_id>/', views.eliminar_factura, name='eliminar_factura'),
    path('buscar-ajax/', views.buscar_facturas_ajax, name='buscar_facturas_ajax'),
    path('export/<str:fmt>/', views.export_facturas, name='export_facturas'),
]
