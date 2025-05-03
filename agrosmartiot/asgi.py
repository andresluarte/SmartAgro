# agrosmartiot/asgi.py

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
import agrosmartiot.routing  # este archivo lo crearemos enseguida

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agrosmartiot.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            agrosmartiot.routing.websocket_urlpatterns
        )
    ),
})
