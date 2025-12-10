# Sistema Bar Galileo 🍺

Sistema integral de gestión para establecimientos de hostelería (bares, restaurantes, cafeterías) desarrollado con Django.

## 📋 Características Principales

- ✅ **Gestión de Productos**: Inventario, categorías, marcas, proveedores
- ✅ **Sistema de Mesas y Pedidos**: Control en tiempo real
- ✅ **Facturación Automatizada**: Generación y gestión de facturas
- ✅ **Control de Gastos**: Registro con comprobantes
- ✅ **Gestión de Nóminas**: Empleados, pagos, bonificaciones
- ✅ **Reportes Avanzados**: PDF, Excel, CSV con gráficos
- ✅ **Sistema de Backups**: Automáticos y manuales
- ✅ **Roles y Permisos**: Control granular de acceso
- ✅ **Notificaciones en Tiempo Real**: WebSockets
- ✅ **Chatbot de Ayuda con IA**: Sistema RAG integrado
- ✅ **Autenticación Google**: Sign-in social

## 🚀 Instalación Rápida

### 1. Clonar el repositorio

```bash
git clone https://github.com/Christian3h/bar-galileo.git
cd bar-galileo
```

### 2. Crear entorno virtual

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias

```powershell
pip install -r requirements.txt

# Para el sistema RAG (chatbot):
pip install -r requirements-rag.txt
```

### 4. Configurar variables de entorno

Crea un archivo `.env` en `bar_galileo/bar_galileo/.env`:

```env
SECRET_KEY=tu_clave_secreta_aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
GOOGLE_API_KEY=tu_google_api_key_aqui
```

### 5. Migraciones de base de datos

```powershell
cd bar_galileo
python manage.py migrate
```

### 6. Crear superusuario

```powershell
python manage.py createsuperuser
```

### 7. Inicializar el Manual de Usuario en el chatbot

```powershell
python manage.py init_manual
```

### 8. Ejecutar servidor

```powershell
python manage.py runserver
```

Accede en: `http://localhost:8000/`

## 📖 Documentación

### Manual de Usuario
Documentación completa del sistema en: **`docs/manual_usuario.md`**

El manual incluye:
- Guía de inicio
- Procedimientos paso a paso
- Descripción de módulos
- Solución de errores
- Preguntas frecuentes

### Integración con Chatbot RAG
Documentación técnica de la integración: **`docs/MANUAL_RAG_INTEGRATION.md`**

## 💬 Chatbot de Ayuda

El sistema incluye un asistente virtual con IA que responde preguntas sobre el manual de usuario.

**Acceso**: `http://localhost:8000/rag-chat/`

**Ejemplos de preguntas**:
- "¿Cómo creo un nuevo producto?"
- "¿Cómo facturo un pedido?"
- "¿Qué permisos tiene el rol de mesero?"

## 🛠️ Tecnologías Utilizadas

- **Backend**: Django 5.2.4, Python 3.x
- **Base de Datos**: SQLite (desarrollo), PostgreSQL (producción recomendada)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **WebSockets**: Django Channels (notificaciones en tiempo real)
- **IA/ML**: Google Gemini API, Sentence Transformers
- **Autenticación**: Django Allauth (Google Sign-in)
- **Reportes**: ReportLab, openpyxl

## 📁 Estructura del Proyecto

```
bar-galileo/
├── bar_galileo/              # Proyecto Django principal
│   ├── accounts/            # Autenticación y cuentas
│   ├── admin_dashboard/     # Panel de administración
│   ├── backups/             # Sistema de backups
│   ├── core/                # Funcionalidad central
│   ├── expenses/            # Gestión de gastos
│   ├── facturacion/         # Sistema de facturación
│   ├── nominas/             # Gestión de nóminas
│   ├── notifications/       # Notificaciones en tiempo real
│   ├── products/            # Gestión de productos
│   ├── rag_chat/            # Chatbot RAG con IA
│   ├── reportes/            # Sistema de reportes
│   ├── roles/               # Roles y permisos
│   ├── tables/              # Mesas y pedidos
│   └── users/               # Gestión de usuarios
├── docs/                    # Documentación
│   ├── manual_usuario.md    # Manual completo del sistema
│   └── MANUAL_RAG_INTEGRATION.md  # Guía técnica RAG
└── requirements.txt         # Dependencias Python
```

## 👥 Roles del Sistema

- **Administrador**: Control total del sistema
- **Gerente**: Gestión operativa y reportes
- **Mesero**: Atención de mesas y pedidos
- **Cajero**: Facturación y caja
- **Cocina**: Visualización de pedidos

## 📊 Módulos Principales

### 1. Productos
- Gestión de inventario
- Categorías, marcas, proveedores
- Control de stock
- Imágenes en formato WebP

### 2. Mesas y Pedidos
- Tablero visual de mesas
- Estados: Disponible, Ocupada, Reservada
- Gestión de pedidos en tiempo real
- Asociación de usuarios a pedidos

### 3. Facturación
- Generación automática de facturas
- Numeración secuencial
- Impresión y descarga PDF
- Descuento automático de stock

### 4. Gastos
- Registro de gastos con categorías
- Adjuntar comprobantes
- Filtros por fecha y categoría

### 5. Nóminas
- Gestión de empleados
- Registro de pagos
- Bonificaciones
- Reportes de nómina

### 6. Reportes
- Ventas, inventario, gastos
- Exportación: PDF, Excel, CSV
- Gráficos y estadísticas
- Reportes programados

### 7. Sistema RAG (Chatbot)
- Asistente virtual con IA
- Búsqueda semántica en documentos
- Respuestas basadas en el manual
- Historial de consultas

## 🔒 Seguridad

- Autenticación robusta con captcha
- Control de permisos por rol
- CSRF protection
- Middleware de seguridad
- Backups automáticos diarios

## 🧪 Testing

```powershell
python manage.py test
```

## 📦 Backups

### Crear backup manual
```powershell
python manage.py dbbackup
```

### Restaurar backup
```powershell
python manage.py dbrestore
```

Los backups automáticos se ejecutan diariamente a las 2:00 AM.

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT.

## 👨‍💻 Autores

- **Christian** - [Christian3h](https://github.com/Christian3h)
- **Felipe** - Colaborador

## 📞 Soporte

Para soporte y consultas:
- Usa el **Chatbot de Ayuda** integrado en el sistema
- Revisa el **Manual de Usuario** en `docs/manual_usuario.md`
- Abre un **Issue** en GitHub

---

**Última actualización**: Diciembre 2025  
**Versión**: 2.0
