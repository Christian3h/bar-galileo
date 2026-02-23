"""
ASGI config for bar_galileo project.
It exposes the ASGI callable as a module-level variable named ``application``.
"""

import os

import notifications.routing
import tables.routing
import users.routing
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bar_galileo.settings")

all_websocket_urlpatterns = (
    notifications.routing.websocket_urlpatterns
    + tables.routing.websocket_urlpatterns
    + users.routing.websocket_urlpatterns
)

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(all_websocket_urlpatterns)  # type: ignore[arg-type]
        ),
    }
)
