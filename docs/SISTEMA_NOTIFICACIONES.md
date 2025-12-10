# Sistema de Notificaciones - Bar Galileo

Este documento explica cómo funciona y cómo utilizar el sistema de notificaciones en tiempo real del proyecto.

## Descripción General

El sistema de notificaciones permite enviar mensajes en tiempo real a usuarios específicos usando **WebSockets** (Django Channels). Las notificaciones se guardan en la base de datos y se muestran como pop-ups flotantes en el navegador.

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                         BACKEND                                  │
├─────────────────────────────────────────────────────────────────┤
│  utils.py          → Función para enviar notificaciones         │
│  models.py         → Modelo Notificacion (BD)                   │
│  consumers.py      → WebSocket Consumer (Channels)              │
│  routing.py        → Rutas WebSocket                            │
│  views.py          → API REST para historial                    │
│  urls.py           → URLs de la API                             │
├─────────────────────────────────────────────────────────────────┤
│                         FRONTEND                                 │
├─────────────────────────────────────────────────────────────────┤
│  notifications.js      → Conexión WebSocket y pop-ups           │
│  notification_history.js → Panel de historial                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Cómo Enviar una Notificación

### 1. Importar la función

```python
from notifications.utils import notificar_usuario
```

### 2. Llamar a la función

```python
notificar_usuario(usuario, mensaje)
```

**Parámetros:**
- `usuario`: Objeto `User` de Django (el usuario que recibirá la notificación)
- `mensaje`: String con el mensaje a mostrar

### 3. Ejemplos de uso

#### Notificación de bienvenida
```python
from notifications.utils import notificar_usuario

if request.user.is_authenticated:
    mensaje = f"¡Bienvenido, {request.user.first_name or request.user.username}!"
    notificar_usuario(request.user, mensaje)
```

#### Notificación al crear un pedido
```python
from notifications.utils import notificar_usuario

def crear_pedido(request):
    # ... lógica de crear pedido ...

    # Notificar al usuario
    notificar_usuario(
        request.user,
        f"Pedido #{pedido.id} creado exitosamente"
    )
```

#### Notificación a otro usuario (ej: administrador)
```python
from django.contrib.auth.models import User
from notifications.utils import notificar_usuario

# Notificar a todos los admins
admins = User.objects.filter(is_superuser=True)
for admin in admins:
    notificar_usuario(admin, "Nuevo pedido recibido en Mesa #5")
```

#### Notificación al aprobar un gasto
```python
from notifications.utils import notificar_usuario

def aprobar_gasto(request, gasto):
    gasto.aprobado = True
    gasto.save()

    # Notificar al creador del gasto
    notificar_usuario(
        gasto.creado_por,
        f"Tu gasto '{gasto.descripcion}' ha sido aprobado"
    )
```

---

## Modelo de Datos

```python
class Notificacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)
```

**Campos:**
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `usuario` | ForeignKey | Usuario destinatario |
| `mensaje` | TextField | Contenido del mensaje |
| `leida` | Boolean | Si fue leída (default: False) |
| `fecha` | DateTime | Fecha de creación automática |

---

## API REST Endpoints

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/notifications/history/` | GET | Obtener historial de notificaciones |
| `/api/notifications/mark-as-read/` | POST | Marcar como leídas |
| `/api/notificaciones/pendientes/` | GET | Obtener notificaciones pendientes |

### Ejemplo: Obtener historial

```javascript
fetch('/api/notifications/history/')
  .then(response => response.json())
  .then(data => {
    console.log('No leídas:', data.unread_count);
    console.log('Historial:', data.history);
  });
```

**Respuesta:**
```json
{
  "unread_count": 3,
  "history": [
    {
      "id": 1,
      "mensaje": "Bienvenido al dashboard",
      "leida": false,
      "fecha": "2025-12-09T10:30:00Z"
    }
  ]
}
```

### Ejemplo: Marcar todas como leídas

```javascript
fetch('/api/notifications/mark-as-read/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({ids: []})  // vacío = todas
});
```

### Ejemplo: Marcar específicas como leídas

```javascript
fetch('/api/notifications/mark-as-read/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({ids: [1, 2, 3]})
});
```

---

## WebSocket

### Conexión
El WebSocket se conecta automáticamente en: `ws://<host>/ws/notificaciones/`

### Flujo
1. Usuario carga la página → JavaScript abre WebSocket
2. Consumer verifica autenticación → Une al grupo `user_{id}`
3. Al llamar `notificar_usuario()` → Se envía mensaje al grupo
4. Frontend recibe mensaje → Muestra pop-up flotante

---

## Configuración Requerida

### settings.py
```python
INSTALLED_APPS = [
    # ...
    'channels',
    'notifications',
]

ASGI_APPLICATION = 'bar_galileo.asgi.application'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
        # Para producción usar Redis:
        # "BACKEND": "channels_redis.core.RedisChannelLayer",
        # "CONFIG": {"hosts": [("127.0.0.1", 6379)]},
    }
}
```

### asgi.py
```python
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import notifications.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            notifications.routing.websocket_urlpatterns
        )
    ),
})
```

---

## Frontend - HTML Requerido

En tu template base, incluir el contenedor de notificaciones flotantes:

```html
<!-- Contenedor para notificaciones flotantes -->
<div id="notificaciones-flotantes"
     style="position: fixed; top: 20px; right: 20px; z-index: 9999;">
</div>

<!-- Scripts -->
<script src="{% static 'js/notifications/notifications.js' %}"></script>
<script src="{% static 'js/admin/notification_history.js' %}"></script>
```

---

## Tips y Buenas Prácticas

### ✅ Hacer
- Usar mensajes cortos y claros
- Notificar acciones importantes (pedidos, pagos, cambios de estado)
- Incluir información relevante (IDs, nombres)

### ❌ Evitar
- No enviar demasiadas notificaciones (fatiga del usuario)
- No enviar información sensible en notificaciones
- No notificar en cada carga de página (causa spam)

### Ejemplo de notificaciones útiles
```python
# ✅ Bueno
notificar_usuario(user, "Pedido #123 completado - Mesa 5")
notificar_usuario(user, "Nuevo backup creado exitosamente")
notificar_usuario(user, "Stock bajo: Solo quedan 5 unidades de 'Cerveza Corona'")

# ❌ Malo
notificar_usuario(user, "Has cargado la página")  # Spam
notificar_usuario(user, "OK")  # No informativo
```

---

## Troubleshooting

### WebSocket no conecta
1. Verificar que Channels esté instalado: `pip install channels`
2. Verificar configuración de `ASGI_APPLICATION` en settings
3. Revisar consola del navegador para errores

### Notificaciones no aparecen
1. Verificar que existe el div `#notificaciones-flotantes`
2. Verificar que los scripts JS están cargados
3. Revisar la consola del navegador

### Notificaciones no se guardan
1. Verificar migraciones: `python manage.py migrate notifications`
2. Verificar que el usuario está autenticado

---

## Archivos del Módulo

```
notifications/
├── __init__.py
├── admin.py          # Registro en admin de Django
├── apps.py           # Configuración de la app
├── consumers.py      # WebSocket Consumer
├── models.py         # Modelo Notificacion
├── routing.py        # Rutas WebSocket
├── urls.py           # URLs API REST
├── utils.py          # Función notificar_usuario()
└── views.py          # Vistas API REST
```
