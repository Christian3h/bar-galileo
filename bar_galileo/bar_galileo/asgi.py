"""
ASGI config for bar_galileo project.

It exposes the ASGI callable as a module-level variable named ``application``.
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bar_galileo.settings")

# Fallback seguro: si Channels o alguna ruta de websockets falla,
# exponemos únicamente la aplicación HTTP estándar para que runserver funcione.
try:
    from channels.routing import ProtocolTypeRouter, URLRouter
    from channels.auth import AuthMiddlewareStack

    websocket_patterns = []
    try:
        import notifications.routing as _notif
        if hasattr(_notif, 'websocket_urlpatterns'):
            websocket_patterns += _notif.websocket_urlpatterns
    except Exception:
        pass

    try:
        import tables.routing as _tables
        if hasattr(_tables, 'websocket_urlpatterns'):
            websocket_patterns += _tables.websocket_urlpatterns
    except Exception:
        pass

    try:
        import users.routing as _users
        if hasattr(_users, 'websocket_urlpatterns'):
            websocket_patterns += _users.websocket_urlpatterns
    except Exception:
        pass

    application = ProtocolTypeRouter({
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(websocket_patterns)
        ),
    })
except Exception:
    # Sin Channels: solo HTTP
    application = get_asgi_application()

