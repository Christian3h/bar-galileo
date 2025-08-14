from django.shortcuts import render

from products.models import Producto

from django.views.generic import ListView
# Create your views here.

class indexView(ListView): 
    model = Producto
    template_name = 'index.html'
    context_object_name = 'productos'