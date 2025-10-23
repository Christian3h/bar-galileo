from roles.models import Module, Action


def crear_modulos_reportes():
    """
    Crea el módulo de reportes y las acciones necesarias en el sistema de permisos.
    """
    # Crear acciones si no existen
    acciones = ['ver', 'crear', 'editar', 'eliminar', 'exportar', 'generar']
    for accion_nombre in acciones:
        Action.objects.get_or_create(nombre=accion_nombre)
    
    # Crear módulo de reportes
    Module.objects.get_or_create(nombre='reportes')
    
    print("✅ Módulo 'reportes' y acciones creados correctamente")
