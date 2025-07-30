from .models import Action, Module
import os
from django.conf import settings

def get_local_apps():
    return [app.split('.')[-1] for app in settings.INSTALLED_APPS if app.startswith('bar_galileo.')]

def crear_modulos_y_acciones():
    acciones = ['ver', 'crear', 'editar', 'eliminar']
    for a in acciones:
        Action.objects.get_or_create(nombre=a)

    modulos = get_local_apps()
    if not modulos:
        modulos = ['productos', 'mesas', 'usuarios', 'reservas', 'proveedores']
    for m in modulos:
        Module.objects.get_or_create(nombre=m)
