#!/bin/bash
# Script para ejecutar el servidor Django con uvicorn y soporte para WebSockets

# Cambiar al directorio del proyecto
cd "$(dirname "$0")"

cd bar_galileo
../.venv/bin/python -m uvicorn bar_galileo.asgi:application --reload --host 0.0.0.0 --port 8000
