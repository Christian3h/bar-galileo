from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('', views.ReporteListView.as_view(), name='reporte_list'),
    path('crear/', views.ReporteCreateView.as_view(), name='reporte_create'),
    path('<int:pk>/', views.ReporteDetailView.as_view(), name='reporte_detail'),
    path('<int:pk>/editar/', views.ReporteUpdateView.as_view(), name='reporte_update'),
    path('<int:pk>/eliminar/', views.ReporteDeleteView.as_view(), name='reporte_delete'),
    path('<int:pk>/exportar/<str:formato>/', views.exportar_reporte, name='reporte_export'),
    path('<int:pk>/generar/', views.generar_reporte_datos, name='reporte_generar'),
]
