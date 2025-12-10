# 🚀 Guía de Inicio Rápido - Sistema Bar Galileo

## ✅ Checklist de Configuración Inicial

Sigue estos pasos para tener el sistema funcionando en minutos:

### 1️⃣ Instalación Base (5 minutos)

```powershell
# Clonar repositorio
git clone https://github.com/Christian3h/bar-galileo.git
cd bar-galileo

# Crear entorno virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Instalar dependencias básicas
pip install -r requirements.txt
```

### 2️⃣ Configuración de Base de Datos (2 minutos)

```powershell
cd bar_galileo

# Ejecutar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser
# Ingresa: usuario, email y contraseña
```

### 3️⃣ Inicializar Datos (Opcional, 3 minutos)

```powershell
# Cargar datos iniciales de ejemplo
python manage.py loaddata initial_data.json

# O crear datos manualmente desde el admin
python manage.py runserver
# Accede a: http://localhost:8000/admin/
```

### 4️⃣ Configurar Variables de Entorno (2 minutos)

Crea el archivo `bar_galileo/bar_galileo/.env`:

```env
SECRET_KEY=django-insecure-tu-clave-secreta-cambiar-en-produccion
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,*

# Opcional: Para Google Sign-in
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=tu_client_id.apps.googleusercontent.com
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=tu_client_secret
```

### 5️⃣ Instalar Chatbot RAG (Opcional, 5-10 minutos)

```powershell
# Instalar dependencias adicionales
pip install -r requirements-rag.txt

# Configurar Google API Key en .env
# GOOGLE_API_KEY=tu_api_key_aqui

# Inicializar el manual en el sistema
python manage.py init_manual
```

### 6️⃣ Iniciar el Servidor (1 minuto)

```powershell
# Desde la carpeta bar_galileo/
python manage.py runserver

# O con Daphne (recomendado para producción):
daphne -b 0.0.0.0 -p 8000 bar_galileo.asgi:application
```

**✅ Listo!** Accede en: `http://localhost:8000/`

---

## 🎯 Primeros Pasos en el Sistema

### 1. Iniciar Sesión

1. Ve a: `http://localhost:8000/`
2. Haz clic en **"Iniciar Sesión"**
3. Ingresa tus credenciales de superusuario
4. Completa el captcha

### 2. Configurar Roles y Permisos

1. Ve a: **Roles > Crear Rol**
2. Crea roles básicos:
   - Mesero
   - Cajero
   - Gerente

3. Asigna permisos según las necesidades

### 3. Crear Usuarios

1. Ve a: **Dashboard > Usuarios**
2. Crea usuarios para cada empleado
3. Asigna roles correspondientes

### 4. Configurar Productos

1. Ve a: **Productos > Categorías**
2. Crea categorías: Bebidas, Comidas, Postres, etc.

3. Ve a: **Productos > Agregar Producto**
4. Completa:
   - Nombre, precio, stock
   - Categoría
   - Imagen (opcional)

### 5. Configurar Mesas

1. Ve a: **Mesas**
2. Crea mesas desde el admin de Django o desde la interfaz

### 6. Probar el Sistema

1. **Crear un pedido**:
   - Selecciona una mesa
   - Agrega productos
   - Guarda el pedido

2. **Facturar**:
   - Abre el pedido
   - Haz clic en "Facturar"
   - Descarga o imprime

3. **Ver reportes**:
   - Ve a **Reportes**
   - Genera un reporte de ventas

4. **Usar el chatbot**:
   - Ve a **Ayuda** o `/rag-chat/`
   - Pregunta: "¿Cómo creo un producto?"

---

## 🔧 Solución de Problemas Comunes

### Error: "No module named 'django'"
**Solución**: Activa el entorno virtual
```powershell
.\.venv\Scripts\Activate.ps1
```

### Error: "Table doesn't exist"
**Solución**: Ejecuta las migraciones
```powershell
python manage.py migrate
```

### Error: "Static files not found"
**Solución**: Recolecta archivos estáticos
```powershell
python manage.py collectstatic
```

### Error: "GOOGLE_API_KEY not configured"
**Solución**: Agrega la key en `.env`:
```env
GOOGLE_API_KEY=tu_api_key_aqui
```

### Chatbot no responde
**Posibles causas**:
1. Manual no inicializado → `python manage.py init_manual`
2. Sin API key de Google → Configura en `.env`
3. Dependencias faltantes → `pip install -r requirements-rag.txt`

---

## 📚 Recursos Útiles

### Documentación
- **Manual de Usuario**: `docs/manual_usuario.md`
- **Integración RAG**: `docs/MANUAL_RAG_INTEGRATION.md`
- **README Principal**: `README.md`

### URLs Importantes
- **Página principal**: `http://localhost:8000/`
- **Admin Django**: `http://localhost:8000/admin/`
- **Chatbot RAG**: `http://localhost:8000/rag-chat/`
- **Dashboard**: `http://localhost:8000/dashboard/`

### Comandos Django Útiles

```powershell
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Recolectar archivos estáticos
python manage.py collectstatic

# Inicializar manual RAG
python manage.py init_manual

# Crear backup
python manage.py dbbackup

# Restaurar backup
python manage.py dbrestore

# Shell de Django
python manage.py shell

# Ver rutas disponibles
python manage.py show_urls
```

---

## 🎓 Datos de Prueba

### Usuario Admin
- **Usuario**: admin
- **Email**: admin@bargalileo.com
- **Contraseña**: (la que creaste)

### Productos de Ejemplo
```python
# En el shell de Django (python manage.py shell)
from products.models import Producto, Categoria

# Crear categoría
cat = Categoria.objects.create(nombre_categoria="Bebidas")

# Crear producto
Producto.objects.create(
    nombre="Coca Cola 350ml",
    precio_compra=1000,
    precio_venta=2000,
    stock=50,
    id_categoria=cat,
    activo=True
)
```

---

## 🚀 Próximos Pasos

1. ✅ **Personaliza el sistema**
   - Cambia logo en `static/img/`
   - Ajusta colores en `static/css/`

2. ✅ **Carga tus productos**
   - Usa el admin o la interfaz

3. ✅ **Configura backups**
   - Programa backups automáticos

4. ✅ **Entrena a tu equipo**
   - Muestra el manual de usuario
   - Explica el chatbot de ayuda

5. ✅ **Monitorea el sistema**
   - Revisa reportes regularmente
   - Verifica historial del chatbot

---

## 💡 Tips Pro

### Rendimiento
- Usa PostgreSQL en producción (no SQLite)
- Configura Redis para caché
- Usa Nginx como proxy inverso

### Seguridad
- Cambia `SECRET_KEY` en producción
- Establece `DEBUG=False` en producción
- Usa HTTPS
- Configura ALLOWED_HOSTS correctamente

### Backups
- Automatiza backups diarios
- Guarda backups en la nube
- Prueba restauraciones periódicamente

### Chatbot
- Mantén el manual actualizado
- Revisa consultas frecuentes
- Agrega FAQs según necesidad

---

**¿Necesitas ayuda?** Usa el chatbot en `/rag-chat/` o revisa `docs/manual_usuario.md`

---

**Tiempo total de configuración**: ~20 minutos  
**Última actualización**: Diciembre 2025
