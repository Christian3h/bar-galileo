# 📦 Sistema de Backups - Bar Galileo

Sistema completo de respaldo automatizado con encriptación GPG para base de datos y archivos media.

## 📋 Tabla de Contenidos

1. [Instalación](#instalación)
2. [Configuración](#configuración)
3. [Uso Rápido](#uso-rápido)
4. [Configuración GPG](#configuración-gpg)
5. [Comandos Disponibles](#comandos-disponibles)
6. [Estructura de Archivos](#estructura-de-archivos)
7. [Solución de Problemas](#solución-de-problemas)
8. [Próximos Pasos](#próximos-pasos)

---

## ✅ Instalación

### Paquetes Instalados
```bash
pip install django-dbbackup==5.0.0 python-gnupg==0.5.5
```

### Apps en INSTALLED_APPS
```python
INSTALLED_APPS = [
    # ...
    'dbbackup',     # Librería django-dbbackup
    'backups',      # App personalizada para gestión
]
```

---

## ⚙️ Configuración

### settings.py

```python
# Storages para Django 5.2+
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
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

# Configuración de Django-DBBackup
DBBACKUP_STORAGE = 'dbbackup'
DBBACKUP_MEDIA_STORAGE = 'mediabackup'
DBBACKUP_MEDIA_PATH = MEDIA_ROOT

# Formato de nombres
DBBACKUP_FILENAME_TEMPLATE = '{datetime}.psql'
DBBACKUP_MEDIA_FILENAME_TEMPLATE = '{datetime}.media.zip'

# Limpieza automática
DBBACKUP_CLEANUP_KEEP = 10
DBBACKUP_CLEANUP_KEEP_MEDIA = 10

# Compresión
DBBACKUP_COMPRESS = True
DBBACKUP_COMPRESSION_LEVEL = 6

# Encriptación GPG
DBBACKUP_ENCRYPTION = True
DBBACKUP_GPG_RECIPIENT = os.getenv('DBBACKUP_GPG_RECIPIENT', 'bargalileo07@gmail.com')
```

### Variables de Entorno (.env)
```bash
DBBACKUP_GPG_RECIPIENT=bargalileo07@gmail.com
```

---

## 🚀 Uso Rápido

### ⭐ Comando Recomendado (Personalizado)

```bash
# Backup completo de DB + Media (encriptado)
python manage.py crear_backup_completo

# Solo base de datos
python manage.py crear_backup_completo --sin-media

# Solo archivos media
python manage.py crear_backup_completo --sin-db
```

**✅ Este comando soluciona el bug de django-dbbackup 5.0.0 que guarda los backups de media en la carpeta incorrecta.**

### Salida del Comando

```
======================================================================
CREANDO BACKUP COMPLETO DE BAR GALILEO
======================================================================

📊 Creando backup de base de datos...
✅ Backup de DB creado: 2025-10-20-214712.psql.gpg
   Tamaño: 86.17 KB

📁 Creando backup de archivos media...
✅ Backup de Media creado: 2025-10-20-214712.media.zip.gpg
   Tamaño: 24.62 MB
   📂 Movido a: backups/backup_files/media/

======================================================================
✅ PROCESO DE BACKUP COMPLETADO
======================================================================

📋 RESUMEN DE BACKUPS DISPONIBLES:

  🗄️  Backups de Base de Datos (3):
     • 2025-10-20-212832 (86.15 KB)
     • 2025-10-20-213017 (86.17 KB)
     • 2025-10-20-214712 (86.17 KB)

  📸 Backups de Media (2):
     • 2025-10-20-213017 (24.62 MB)
     • 2025-10-20-214712 (24.62 MB)
```

---

## 🔐 Configuración GPG

### 1. Verificar Instalación de GPG
```bash
gpg --version
# Debe mostrar GPG 2.x o superior
```

### 2. Generar Clave GPG (Solo primera vez)
```bash
gpg --full-generate-key
```

**Opciones recomendadas:**
- Tipo: `(1) RSA and RSA`
- Tamaño: `4096` bits
- Validez: `0` (no expira)
- Nombre: `Bar Galileo Backups`
- Email: `bargalileo07@gmail.com`
- Contraseña: **¡Guárdala en lugar seguro!**

### 3. Listar Claves
```bash
gpg --list-keys
```

Salida esperada:
```
pub   rsa4096 2025-10-20 [SC]
      E83D59F6FA84D04B... (ID de la clave)
uid           [ultimate] Bar Galileo Backups <bargalileo07@gmail.com>
sub   rsa4096 2025-10-20 [E]
```

### 4. Exportar y Respaldar Claves (¡IMPORTANTE!)

**Clave Pública:**
```bash
gpg --armor --export bargalileo07@gmail.com > bar-galileo-public.asc
```

**Clave Privada (GUARDAR EN LUGAR MUY SEGURO):**
```bash
gpg --armor --export-secret-keys bargalileo07@gmail.com > bar-galileo-private.asc
```

⚠️ **ADVERTENCIA**: Sin la clave privada, NO podrás desencriptar los backups.

### 5. Importar Claves (En otro servidor)
```bash
# Importar clave pública
gpg --import bar-galileo-public.asc

# Importar clave privada
gpg --import bar-galileo-private.asc
```

---

## 📋 Comandos Disponibles

### Crear Backups

```bash
# Recomendado: Comando personalizado
python manage.py crear_backup_completo

# Alternativos (comandos individuales)
python manage.py dbbackup --encrypt
python manage.py mediabackup --encrypt
```

### Restaurar Backups

```bash
# Restaurar base de datos (pedirá contraseña GPG)
python manage.py dbrestore

# Restaurar archivos media
python manage.py mediarestore

# Restaurar desde archivo específico
python manage.py dbrestore --input-filename=2025-10-20-214712.psql.gpg
```

### Listar Backups

```bash
# Ver backups de base de datos
ls -lh backups/backup_files/db/

# Ver backups de media
ls -lh backups/backup_files/media/
```

### Desencriptar Manualmente

```bash
# Desencriptar backup de DB
gpg --decrypt backups/backup_files/db/2025-10-20-214712.psql.gpg > backup.psql

# Desencriptar backup de media
gpg --decrypt backups/backup_files/media/2025-10-20-214712.media.zip.gpg > backup.tar
tar -xf backup.tar
```

---

## 📁 Estructura de Archivos

```
bar_galileo/backups/
├── backup_files/
│   ├── db/                      # Backups de base de datos (.psql.gpg)
│   │   ├── 2025-10-20-214712.psql.gpg
│   │   └── ...
│   └── media/                   # Backups de archivos media (.media.zip.gpg)
│       ├── 2025-10-20-214712.media.zip.gpg
│       └── ...
├── management/
│   └── commands/
│       └── crear_backup_completo.py  # Comando personalizado
├── templates/
│   └── backups/                 # Templates para interfaz web (pendiente)
├── models.py
├── views.py                     # Vistas (pendiente)
├── urls.py                      # URLs (pendiente)
└── README.md                    # Este archivo
```

### Contenido de los Backups

**Backup de Base de Datos:**
- Formato: `.psql.gpg` (SQLite encriptado)
- Tamaño: ~86 KB
- Contenido: Toda la base de datos (`db.sqlite3`)

**Backup de Media:**
- Formato: `.media.zip.gpg` (TAR encriptado)
- Tamaño: ~25 MB
- Contenido:
  - 📸 Imágenes de productos (`media/productos/`)
  - 👤 Avatares de usuarios (`media/img/avatar/`)
  - 📄 Recibos (`media/receipts/`)

---

## 🔧 Solución de Problemas

### Error: "No module named 'dbbackup'"
```bash
# Instalar en el entorno virtual correcto
.venv/bin/pip install django-dbbackup==5.0.0 python-gnupg==0.5.5
```

### Error: "gpg: no valid OpenPGP data found"
- Verifica que la clave GPG esté configurada
- Confirma que `DBBACKUP_GPG_RECIPIENT` sea correcto

### Error: "gpg: decryption failed: No secret key"
- No tienes la clave privada necesaria
- Importa la clave: `gpg --import bar-galileo-private.asc`

### Los backups de media se guardan en /db/
- Usa el comando personalizado: `python manage.py crear_backup_completo`
- Mueve manualmente: `mv backups/backup_files/db/*.media.zip.gpg backups/backup_files/media/`

### Las imágenes no aparecen después de migrar a media/
1. Verifica que `MEDIA_URL` y `MEDIA_ROOT` estén configurados
2. Verifica que las URLs incluyan: `+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)`
3. Limpia la caché del navegador (Ctrl+Shift+R)
4. Limpia la caché de Python: `find . -type d -name "__pycache__" -exec rm -rf {} +`

---

## 📝 Próximos Pasos

- [ ] Implementar vistas basadas en clases (CBVs)
- [ ] Crear URLs para la app backups
- [ ] Crear templates para interfaz web
- [ ] Implementar permisos con decoradores
- [ ] Agregar funcionalidad de descarga de backups
- [ ] Programación automática de backups (cron/celery)
- [ ] Almacenamiento en la nube (S3, Google Cloud)

---

## 🔒 Seguridad

- ✅ Todos los backups se encriptan con GPG
- ✅ Los archivos de backup no se suben a git (`.gitignore`)
- ⚠️ Guarda tu clave privada GPG en un lugar seguro
- ⚠️ Sin la clave privada, los backups son irrecuperables
- ⚠️ Documenta quién tiene acceso a las claves GPG

---

## 📚 Documentación

- [Django-DBBackup](https://django-dbbackup.readthedocs.io/)
- [GNU Privacy Guard](https://gnupg.org/documentation/)
- [Django File Storage](https://docs.djangoproject.com/en/5.2/topics/files/)

---

**Última actualización:** 20 de Octubre, 2025
**Versión:** 1.0
**Mantenedor:** Christian (@Christian3h)
