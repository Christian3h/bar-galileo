from .models import Action, Module
import os
from django.conf import settings

def get_local_apps():
    return [app.split('.')[-1] for app in settings.INSTALLED_APPS if app.startswith('bar_galileo.')]

def crear_modulos_y_acciones():
    acciones = ['ver', 'crear', 'editar', 'eliminar']
    for a in acciones:
        Action.objects.get_or_create(nombre=a)

    modulos_a_crear = get_local_apps()
    if not modulos_a_crear:
        modulos_a_crear = ['products', 'tables', 'users', 'reservations', 'providers', 'brands', 'roles', 'categories', 'dashboard', 'expenses', 'nominas']
    for m in modulos_a_crear:
        Module.objects.get_or_create(nombre=m)
from roles.models import Module, Action, Role

