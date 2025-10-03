#!/usr/bin/env python3
"""
Script avanzado para ejecutar el servidor Django con uvicorn.
Usa configuración personalizada para vigilar archivos HTML, CSS, JS y Python.
"""

import os
import sys
import subprocess
from pathlib import Path

# Agregar el directorio del proyecto al path
project_dir = Path(__file__).parent / "bar_galileo"
sys.path.insert(0, str(project_dir))

# Importar configuración del watcher
try:
    from watcher import get_reload_dirs, get_reload_includes, get_reload_excludes
except ImportError:
    print("⚠️  No se pudo importar la configuración del watcher. Usando configuración básica.")
    get_reload_dirs = lambda: [str(project_dir)]
    get_reload_includes = lambda: ["*.py", "*.html", "*.css", "*.js"]
    get_reload_excludes = lambda: ["*.pyc", "__pycache__/*"]

def run_server():
    """Ejecuta el servidor uvicorn con configuración avanzada de vigilancia."""
    
    print("🚀 Iniciando servidor Bar Galileo con vigilancia extendida...")
    print("📁 Vigilando archivos: Python, HTML, CSS, JavaScript, JSON")
    print("🔄 El servidor se reiniciará automáticamente al detectar cambios")
    print("-" * 60)
    
    # Cambiar al directorio del proyecto
    os.chdir(project_dir)
    
    # Obtener configuración
    reload_dirs = get_reload_dirs()
    reload_includes = get_reload_includes()
    reload_excludes = get_reload_excludes()
    
    # Construir comando uvicorn
    cmd = [
        sys.executable, "-m", "uvicorn",
        "bar_galileo.asgi:application",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000",
    ]
    
    # Agregar directorios a vigilar
    for dir_path in reload_dirs:
        if Path(dir_path).exists():
            cmd.extend(["--reload-dir", dir_path])
    
    # Agregar patrones de inclusión
    for pattern in reload_includes:
        cmd.extend(["--reload-include", pattern])
    
    # Agregar patrones de exclusión
    for pattern in reload_excludes:
        cmd.extend(["--reload-exclude", pattern])
    
    print(f"💻 Comando: {' '.join(cmd)}")
    print("-" * 60)
    
    try:
        # Ejecutar el servidor
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al ejecutar el servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Verificar que estamos en el entorno virtual
    venv_path = Path(__file__).parent / ".venv"
    if venv_path.exists() and str(venv_path) not in sys.executable:
        print("⚠️  Recomendación: Ejecuta este script desde el entorno virtual")
        print(f"   Activar: source {venv_path}/bin/activate")
        print()
    
    run_server()
