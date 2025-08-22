# 🔄 Auto-reload de Archivos HTML/CSS/JS en Bar Galileo

Este proyecto incluye configuración avanzada para que uvicorn vigile archivos HTML, CSS y JavaScript además de los archivos Python, permitiendo reinicio automático del servidor cuando modificas templates o estilos.

## 📁 Archivos Creados

### 1. `bar_galileo/watcher.py`
Configuración personalizada que define:
- Directorios a vigilar
- Tipos de archivos a incluir (*.py, *.html, *.css, *.js, *.json)
- Archivos a excluir (cache, logs, etc.)

### 2. `run_server.sh` (Modificado)
Script bash mejorado con opciones de vigilancia extendida.

### 3. `run_server_advanced.py` (Nuevo)
Script Python avanzado que usa la configuración del watcher.

## 🚀 Formas de Ejecutar el Servidor

### Opción 1: Script Bash Básico (Recomendado)
```bash
./run_server.sh
```

### Opción 2: Script Python Avanzado
```bash
python run_server_advanced.py
```

### Opción 3: Comando Manual
```bash
cd bar_galileo
uvicorn bar_galileo.asgi:application \
    --reload \
    --host 0.0.0.0 \
    --port 8000 \
    --reload-include="*.py" \
    --reload-include="*.html" \
    --reload-include="*.css" \
    --reload-include="*.js" \
    --reload-include="*.json"
```

## 📋 Tipos de Archivos Vigilados

✅ **Incluidos** (reinician el servidor):
- `*.py` - Archivos Python
- `*.html` - Templates Django
- `*.css` - Hojas de estilo
- `*.js` - JavaScript
- `*.json` - Archivos de configuración

❌ **Excluidos** (no reinician el servidor):
- `*.pyc` - Bytecode Python compilado
- `*.pyo` - Archivos optimizados Python
- `__pycache__/*` - Cache de Python
- `.git/*` - Archivos de Git
- `*.log` - Archivos de log
- `db.sqlite3` - Base de datos SQLite

## 📂 Directorios Vigilados

El sistema vigila automáticamente:
- Directorio principal del proyecto
- Todos los directorios de apps Django
- Subdirectorios `templates/` y `static/` de cada app
- Directorio `staticfiles/`

## 🔍 Verificación

Para verificar que funciona:

1. Ejecuta el servidor: `./run_server.sh`
2. Modifica cualquier archivo HTML, CSS o JS
3. Observa en la consola el mensaje de reinicio automático
4. El servidor se reinicia sin perder la configuración

## 🎯 Beneficios

- **No más parar/iniciar manual**: El servidor se reinicia automáticamente
- **Desarrollo más ágil**: Cambios en frontend se aplican inmediatamente
- **Mayor productividad**: Menos interrupciones en el flujo de trabajo
- **Vigilancia inteligente**: Solo archivos relevantes disparan el reinicio

## ⚠️ Nota Importante

El reinicio automático del servidor no refresca automáticamente el navegador. Para eso necesitarías:
- Extensión de navegador para auto-refresh
- Configurar live-reload con Django-extensions
- Usar herramientas como Browser-sync

Pero al menos ya no tienes que parar y correr el servidor manualmente cada vez que cambias un template o CSS! 🎉
