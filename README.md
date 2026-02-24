# 🍸 Bar Galileo

Sistema de gestión integral para Bar Galileo - Sogamoso, Boyacá, Colombia.

![Django](https://img.shields.io/badge/Django-5.2.4-green)
![Python](https://img.shields.io/badge/Python-3.13-blue)
![MySQL](https://img.shields.io/badge/MySQL-MariaDB-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 📋 Descripción

Bar Galileo es una aplicación web completa para la gestión de un bar/restaurante que incluye:

- 🪑 **Gestión de Mesas y Pedidos** - Control de mesas, pedidos y facturación
- 📦 **Inventario de Productos** - Gestión de productos, categorías, marcas y proveedores
- 👥 **Gestión de Usuarios** - Sistema de roles y permisos personalizado
- 💰 **Control de Gastos** - Registro y seguimiento de gastos
- 👷 **Nóminas** - Gestión de empleados y pagos
- 📊 **Reportes** - Generación de reportes en PDF y Excel
- 🔔 **Notificaciones** - Sistema de notificaciones en tiempo real con WebSockets
- 💾 **Backups** - Sistema de copias de seguridad automáticas
- 🤖 **RAG Chat** - Asistente inteligente con IA para consultas sobre documentos

## 🛠️ Tecnologías

| Categoría | Tecnología |
|-----------|------------|
| **Backend** | Django 5.2.4, Python 3.13 |
| **Base de datos** | MySQL/MariaDB |
| **Frontend** | HTML5, CSS3, JavaScript |
| **WebSockets** | Django Channels, Daphne |
| **Autenticación** | Django Allauth (Google OAuth) |
| **Exportación** | ReportLab (PDF), OpenPyXL (Excel) |
| **IA/RAG** | Sentence Transformers, FAISS |

## 📁 Estructura del Proyecto

```
bar-galileo/
├── bar_galileo/           # Proyecto Django principal
│   ├── accounts/          # Autenticación y cuentas
│   ├── admin_dashboard/   # Panel de administración
│   ├── backups/           # Sistema de backups
│   ├── core/              # Páginas principales
│   ├── expenses/          # Gestión de gastos
│   ├── facturacion/       # Facturación
│   ├── nominas/           # Gestión de nóminas
│   ├── notifications/     # Notificaciones WebSocket
│   ├── products/          # Gestión de productos
│   ├── rag_chat/          # Chat con IA
│   ├── reportes/          # Generación de reportes
│   ├── roles/             # Sistema de roles y permisos
│   ├── tables/            # Gestión de mesas y pedidos
│   └── users/             # Perfiles de usuario
├── docs/                  # Documentación
└── requirements.txt       # Dependencias
```

## 🚀 Despliegue con Docker

La pila se compone de dos servicios definidos en `docker-compose.yml`:

| Servicio | Detalle |
|----------|---------|
| `web` | Imagen propia basada en `python:3.12-slim`, instala `requirements-docker.txt`, corre migrations/collectstatic y expone Django + Channels mediante `daphne` en el puerto 8000. |
| `db` | MySQL 8.0 con autenticación `mysql_native_password`, datos persistentes en el volumen `db_data`. |

### 1. Configurar variables de entorno
- Edita `.env.docker` (incluye valores seguros de desarrollo). Define aquí `GOOGLE_API_KEY`, credenciales SMTP (`EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`) y, si lo deseas, una nueva `SECRET_KEY` y `ALLOWED_HOSTS`.
- Los valores se inyectan automáticamente tanto en el contenedor `web` como en `db`, y Django también los lee vía `os.getenv`.

### 2. Construir y levantar
```bash
# Construir imágenes y descargar MySQL
docker compose up -d --build

# Seguir logs del servicio web
docker compose logs -f web
```

La aplicación quedará disponible en http://localhost:8000 (estático y media persisten en volúmenes `static_volume` y `media_volume`).

### 3. Operaciones frecuentes
```bash
# Aplicar migraciones (entrypoint ya lo hace, pero puedes forzarlo)
docker compose exec web python bar_galileo/manage.py migrate

# Crear superusuario
docker compose exec web python bar_galileo/manage.py createsuperuser

# Sembrar datos de ejemplo
docker compose exec web python bar_galileo/manage.py seed_fake_data

# Ejecutar comandos para el CAPTCHA de audio
docker compose exec web which flite
docker compose exec web flite -t "prueba audio" -o /tmp/test.wav

# Generar reporte de licencias
docker compose exec web pip-licenses --with-authors --with-urls --format=markdown \
	> /app/bar_galileo/docs/THIRD_PARTY_LICENSES.md
```

### 4. Limpieza y apagado
```bash
# Detener servicios
docker compose down

# Detener y borrar volúmenes (incluye DB)
docker compose down -v
```

## 🚀 Instalación (modo manual)

### Requisitos previos

- Python 3.11+
- MySQL/MariaDB
- Node.js (opcional, para desarrollo frontend)

### Pasos de instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/Christian3h/bar-galileo.git
cd bar-galileo
```

2. **Crear entorno virtual**
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar base de datos MySQL**
```bash
sudo mysql -u root
```
```sql
CREATE DATABASE bar_galileo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'bar_galileo_user'@'localhost' IDENTIFIED BY 'tu_contraseña';
GRANT ALL PRIVILEGES ON bar_galileo.* TO 'bar_galileo_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

5. **Configurar variables de entorno**

Crear archivo `bar_galileo/bar_galileo/.env`:
```env
secret_key=tu_clave_secreta
DB_NAME=bar_galileo
DB_USER=bar_galileo_user
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_PORT=3306
DEBUG=True
```

6. **Ejecutar migraciones**
```bash
cd bar_galileo
python manage.py migrate
```

7. **Crear superusuario**
```bash
python manage.py createsuperuser
```

8. **Ejecutar servidor**
```bash
python manage.py runserver
```

Visita `http://localhost:8000`

## 📖 Documentación

Consulta la carpeta `docs/` para documentación detallada:

- [Sistema de Backups](docs/BACKUPS_IMPLEMENTATION.md)
- [Sistema de Notificaciones](docs/SISTEMA_NOTIFICACIONES.md)
- [Guía de Reportes](docs/REPORTES_GUIA_USUARIO.md)
- [Exportación de Datos](docs/SOLUCION_EXPORTACION.md)

## 👥 Equipo de Desarrollo

- **Christian** - Desarrollador principal
- **Jorge Alfredo Arismendy Zambrano** - Desarrollador
- **Sebastian** - Desarrollador
- **Felipe** - Desarrollador

## 📍 Contacto

- **Bar Galileo**
- 📍 Sogamoso, Boyacá, Colombia
- 📞 +57 322-227-1308
- 📧 bargalileo07@gmail.com

## 📄 Licencia

Este proyecto es privado y pertenece a Bar Galileo.

---

⭐ **Bar Galileo** - Creamos experiencias únicas en coctelería premium
