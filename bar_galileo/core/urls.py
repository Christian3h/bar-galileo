from django.urls import path
from .views import indexView, ProductosAjaxView

urlpatterns = [
    path('', indexView.as_view(), name='index'),
    path('productos/ajax/', ProductosAjaxView.as_view(), name='productos_ajax'),
]