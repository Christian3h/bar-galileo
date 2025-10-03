from django.urls import path
<<<<<<< HEAD
from .views import indexView, ProductosAjaxView, StoreView

urlpatterns = [
    path('', indexView.as_view(), name='index'),
    path('productos/ajax/', ProductosAjaxView.as_view(), name='productos_ajax'),
    path('store/', StoreView.as_view(), name='store'),
=======
from .views import indexView

urlpatterns = [
    path('', indexView.as_view(), name='index'),
>>>>>>> f550aac13c0202e2f4652738b7d329dd256a899a
]