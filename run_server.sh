#!/bin/bash
# Script para ejecutar el servidor Django con uvicorn y soporte para WebSockets
# Incluye vigilancia de archivos HTML, CSS y JS para reinicio automático

# Cambiar al directorio del proyecto
cd "$(dirname "$0")"

cd bar_galileo

# Ejecutar uvicorn con vigilancia extendida de archivos
../.venv/bin/python -m uvicorn bar_galileo.asgi:application \
    --reload \
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
