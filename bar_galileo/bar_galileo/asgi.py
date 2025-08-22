"""
ASGI config for bar_galileo project.

It exposes the ASGI callable as a module-level variable named ``application``.
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import notifications.routing
import tables.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bar_galileo.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            notifications.routing.websocket_urlpatterns + 
            tables.routing.websocket_urlpatterns
        )
    ),
})

