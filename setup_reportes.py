#!/usr/bin/env python
"""
Script para configurar el módulo de reportes en el sistema de roles y permisos
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bar_galileo'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bar_galileo.settings')
django.setup()

from roles.models import Module, Action

def setup_reportes():
    """Crear el módulo de reportes y sus acciones"""
    
    # Crear módulo de reportes
    reportes_module, created = Module.objects.get_or_create(nombre='reportes')
    if created:
        print("✓ Módulo 'reportes' creado exitosamente")
    else:
        print("✓ Módulo 'reportes' ya existe")
    
    # Crear las acciones básicas si no existen
    acciones = ['ver', 'crear', 'editar', 'eliminar']
    for accion_nombre in acciones:
        accion, created = Action.objects.get_or_create(nombre=accion_nombre)
        if created:
            print(f"✓ Acción '{accion_nombre}' creada")
        else:
            print(f"✓ Acción '{accion_nombre}' ya existe")
    
    print("\n" + "="*60)
    print("CONFIGURACIÓN COMPLETADA")
    print("="*60)
    print("\nAhora puedes:")
    print("1. Ir al panel de Roles y Permisos en el dashboard")
    print("2. Editar un rol (por ejemplo, 'Administrador')")
    print("3. Asignar los permisos del módulo 'reportes' al rol")
    print("4. Los usuarios con ese rol podrán ver el módulo en el menú")
    print("\n" + "="*60)

if __name__ == '__main__':
    setup_reportes()
