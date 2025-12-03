from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('', views.ReporteListView.as_view(), name='reporte_list'),
    path('nuevo/', views.ReporteCreateView.as_view(), name='reporte_create'),
    path('detalle/<int:pk>/', views.ReporteDetailView.as_view(), name='reporte_detail'),
    path('editar/<int:pk>/', views.ReporteUpdateView.as_view(), name='reporte_update'),
    path('eliminar/<int:pk>/', views.ReporteDeleteView.as_view(), name='reporte_delete'),
    path('exportar/<int:pk>/<str:formato>/', views.exportar_reporte, name='exportar_reporte'),
    path('generar/<int:pk>/', views.generar_reporte_datos, name='generar_reporte'),
]
