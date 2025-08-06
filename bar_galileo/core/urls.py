from django.urls import path
from .views import indexView, index

urlpatterns = [
    path('', index, name='index'),
]