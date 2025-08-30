from django.urls import path
from .views import indexView, ProductosAjaxView, StoreView

urlpatterns = [
    path('', indexView.as_view(), name='index'),
    path('productos/ajax/', ProductosAjaxView.as_view(), name='productos_ajax'),
    path('store/', StoreView.as_view(), name='store'),
]