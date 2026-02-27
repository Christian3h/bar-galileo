# Solución: Copias de Seguridad No Funcionaban

## Problema Identificado

Las copias de seguridad (completa, solo BD, solo media) no funcionaban debido a dos problemas:

### 1. GPG no estaba instalado en el sistema
El sistema estaba configurado para encriptar los backups con GPG, pero GPG no estaba instalado en macOS.

### 2. El módulo python-gnupg no estaba instalado
Aunque estaba listado en `requirements.txt`, no se había instalado en el entorno virtual.

### 3. El entorno virtual no se estaba usando correctamente
En algunos casos, los comandos se ejecutaban con el Python de conda base en lugar del Python del entorno virtual del proyecto.

## Solución Implementada

### Paso 1: Instalación de GPG
```bash
# Instalar GPG usando Homebrew
brew install gnupg
```

### Paso 2: Generación de Clave GPG
Se generó una clave GPG para el email configurado en el proyecto:
```bash
gpg --batch --gen-key <<EOF
%no-protection
Key-Type: RSA
Key-Length: 2048
Name-Real: Bar Galileo Backups
Name-Email: bargalileo07@gmail.com
Expire-Date: 0
%commit
EOF
```

### Paso 3: Instalación de python-gnupg
```bash
# Se instaló el módulo Python en el entorno virtual
pip install python-gnupg
```

### Paso 4: Actualización de Configuración
Se actualizó la configuración de django-dbbackup en `settings.py` para ser compatible con la versión 5.0.0+:

```python
# Se removieron las configuraciones deprecadas DBBACKUP_STORAGE
# Se mantuvieron solo las definiciones en STORAGES
STORAGES = {
    "dbbackup": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {
            "location": str(BASE_DIR / "backups" / "backup_files" / "db"),
        },
    },
    "mediabackup": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {
            "location": str(BASE_DIR / "backups" / "backup_files" / "media"),
        },
    },
}
```

## Verificación de la Solución

### Probar Backup de Base de Datos
```bash
python manage.py crear_backup_completo --sin-media
```

### Probar Backup de Archivos Media
```bash
python manage.py crear_backup_completo --sin-db
```

### Probar Backup Completo
```bash
python manage.py crear_backup_completo
```

## Importante: Uso del Entorno Virtual

### Para ejecutar el servidor (RECOMENDADO)
Siempre usa el script proporcionado que utiliza el entorno virtual correcto:
```bash
./run_server.sh
```

### Si necesitas ejecutar comandos manualmente
Asegúrate de activar el entorno virtual primero:
```bash
source .venv/bin/activate
python manage.py <comando>
```

O usa la ruta completa al Python del venv:
```bash
.venv/bin/python manage.py <comando>
```

## Archivos Modificados

1. **bar_galileo/bar_galileo/settings.py**
   - Actualizada la configuración de STORAGES para django-dbbackup 5.0.0+
   - Removidas configuraciones deprecadas

2. **bar_galileo/backups/views.py**
   - Mejorado el manejo de errores para detectar módulos faltantes
   - Mensajes de error más informativos

## Mantenimiento

### Verificar que GPG está instalado
```bash
gpg --version
```

### Verificar la clave GPG
```bash
gpg --list-keys bargalileo07@gmail.com
```

### Verificar python-gnupg en el venv
```bash
.venv/bin/python -c "import gnupg; print(gnupg.__version__)"
```

## Estado Actual

✅ GPG instalado y configurado
✅ Clave GPG generada para bargalileo07@gmail.com
✅ python-gnupg instalado en el entorno virtual
✅ Configuración de django-dbbackup actualizada
✅ Backups funcionando correctamente (DB, Media y Completo)

## Fecha de Resolución
11 de febrero de 2026
