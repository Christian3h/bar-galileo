"""
ASGI config for bar_galileo project.

It exposes the ASGI callable as a module-level variable named ``application``.
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
<<<<<<< HEAD
import notifications.routing
import tables.routing
import users.routing
=======
import notifications.routing  # Cambia 'notificaciones' por tu app real
>>>>>>> f550aac13c0202e2f4652738b7d329dd256a899a

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bar_galileo.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
<<<<<<< HEAD
            notifications.routing.websocket_urlpatterns + 
            tables.routing.websocket_urlpatterns +
            users.routing.websocket_urlpatterns
=======
            notifications.routing.websocket_urlpatterns
>>>>>>> f550aac13c0202e2f4652738b7d329dd256a899a
        )
    ),
})

