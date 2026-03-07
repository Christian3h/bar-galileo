# Solución al Problema de Creación de Backups

## Problema Identificado

El sistema de copias de seguridad no estaba funcionando correctamente debido a que:

1. **Faltaba el módulo `python-gnupg`**: Aunque estaba en `requirements.txt`, no estaba instalado en el entorno.
2. **GPG se colgaba**: La encriptación GPG requiere una clave configurada, y sin ella el proceso se quedaba bloqueado indefinidamente.

## Solución Implementada

### 1. Instalación del módulo python-gnupg
```bash
pip install python-gnupg
```

### 2. Deshabilitación de encriptación GPG por defecto

Se modificó el archivo `bar_galileo/settings.py` para deshabilitar la encriptación:

```python
# Antes:
DBBACKUP_ENCRYPTION = True
DBBACKUP_GPG_RECIPIENT = 'bargalileo07@gmail.com'

# Ahora:
DBBACKUP_ENCRYPTION = False
# DBBACKUP_GPG_RECIPIENT = 'bargalileo07@gmail.com'
```

### 3. Actualización del comando `crear_backup_completo`

El comando ahora detecta automáticamente si la encriptación está habilitada y ajusta su comportamiento:

- Si `DBBACKUP_ENCRYPTION = True`: Crea archivos `.psql.gpg` y `.media.zip.gpg`
- Si `DBBACKUP_ENCRYPTION = False`: Crea archivos `.psql` y `.media.zip`

### 4. Actualización de las vistas

Las vistas ahora buscan archivos con ambos patrones (con y sin `.gpg`), permitiendo listar todos los backups independientemente del método de encriptación.

### 5. Actualización de templates

Los templates ahora aceptan archivos con y sin encriptación para restauración.

## Pruebas Realizadas

✅ **Backup completo (DB + Media)**: Funciona correctamente
```bash
python manage.py crear_backup_completo
```

✅ **Backup solo base de datos**: Funciona correctamente
```bash
python manage.py crear_backup_completo --sin-media
```

✅ **Backup solo archivos media**: Funciona correctamente  
```bash
python manage.py crear_backup_completo --sin-db
```

## Resultados

Los backups ahora se crean exitosamente en:
- **Base de datos**: `backups/backup_files/db/2026-02-11-102923.psql` (216 KB)
- **Archivos media**: `backups/backup_files/media/2026-02-11-102923.media.zip` (33 MB)

## Cómo Habilitar Encriptación (Opcional)

Si deseas habilitar la encriptación GPG en el futuro:

1. **Generar clave GPG**:
```bash
gpg --gen-key
# Usar el email: bargalileo07@gmail.com
```

2. **Habilitar en settings.py**:
```python
DBBACKUP_ENCRYPTION = True
DBBACKUP_GPG_RECIPIENT = 'bargalileo07@gmail.com'
```

3. Los backups se crearán automáticamente con encriptación GPG.

## Archivos Modificados

- ✏️ `bar_galileo/bar_galileo/settings.py`
- ✏️ `bar_galileo/backups/management/commands/crear_backup_completo.py`
- ✏️ `bar_galileo/backups/views.py`
- ✏️ `bar_galileo/backups/templates/backups/backup_list.html`

## Fecha de Implementación

11 de febrero de 2026
