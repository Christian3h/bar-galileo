from django.urls import path
from  .views import DashboardView, export_dashboard

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('export/<str:fmt>/', export_dashboard, name='export_dashboard'),
]