#!/bin/bash
# Script para ejecutar el servidor Django con uvicorn y soporte para WebSockets
# Incluye vigilancia de archivos HTML, CSS y JS para reinicio automático

# --- Detección de IP y muestra de URL ---
# Obtener la IP local de la manera más fiable (compatible macOS)
LOCAL_IP=$(ipconfig getifaddr en0)

# Limpiar la pantalla y mostrar información ótil
clear
echo "======================================================"
echo "             Servidor Bar Galileo"
echo "======================================================"

echo ""
echo "Iniciando servidor Uvicorn con recarga automática..."

echo ""
echo "Puedes acceder desde este equipo en:"
echo "  http://localhost:8000"
echo "  http://127.0.0.1:8000"

echo ""
echo "Desde otros dispositivos en la misma red, usa:"
echo "  http://${LOCAL_IP}:8000"

echo ""
echo "======================================================"
echo "Presiona CTRL+C para detener el servidor."

# --- Fin de la sección de información ---


# Cambiar al directorio del proyecto
cd "$(dirname "$0")"

cd bar_galileo

# Ejecutar uvicorn con vigilancia extendida de archivos
../.venv/bin/python -m uvicorn bar_galileo.asgi:application \
    --host 0.0.0.0 \
    --port 8000 \
    --reload-include="*.py" \
    --reload-include="*.html" \
    --reload-include="*.css" \
    --reload-include="*.js" \
    --reload-include="*.json" \
    --reload-exclude="*.pyc" \
    --reload-exclude="*.pyo" \
    --reload-exclude="__pycache__/*" \
    --reload-exclude=".git/*" \
    --reload-exclude="*.log" \
    --reload-exclude="db.sqlite3"