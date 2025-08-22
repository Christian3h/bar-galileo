"""
Configuración de archivos para vigilar con uvicorn.
Este archivo define qué tipos de archivos deben ser vigilados para reiniciar el servidor.
"""

import os
from pathlib import Path

def get_reload_dirs():
    """
    Retorna los directorios que uvicorn debe vigilar para cambios.
    """
    base_dir = Path(__file__).parent
    
    reload_dirs = [
        str(base_dir),  # Directorio del proyecto Django
        str(base_dir / "templates"),  # Templates específicos
        str(base_dir / "static"),     # Archivos estáticos
        str(base_dir / "staticfiles"), # Archivos estáticos recolectados
    ]
    
    # Agregar directorios de apps que existan
    app_dirs = [
        "core", "products", "tables", "notifications", 
        "roles", "users", "admin_dashboard", "accounts"
    ]
    
    for app_dir in app_dirs:
        app_path = base_dir / app_dir
        if app_path.exists():
            reload_dirs.append(str(app_path))
            # Agregar subdirectorios de templates y static si existen
            if (app_path / "templates").exists():
                reload_dirs.append(str(app_path / "templates"))
            if (app_path / "static").exists():
                reload_dirs.append(str(app_path / "static"))
    
    return reload_dirs

def get_reload_includes():
    """
    Retorna los patrones de archivos que deben ser vigilados.
    """
    return [
        "*.py",      # Archivos Python
        "*.html",    # Templates HTML
        "*.css",     # Hojas de estilo
        "*.js",      # JavaScript
        "*.json",    # Archivos de configuración JSON
    ]

def get_reload_excludes():
    """
    Retorna los patrones de archivos que NO deben ser vigilados.
    """
    return [
        "*.pyc",
        "*.pyo", 
        "__pycache__/*",
        ".git/*",
        "node_modules/*",
        "*.log",
        ".env",
        "db.sqlite3",
    ]
