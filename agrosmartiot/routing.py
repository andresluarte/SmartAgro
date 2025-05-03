# agrosmartiot/routing.py

from django.urls import re_path
from agrosmartiot.consumers import SensorDataConsumer  # este lo crearemos enseguida

websocket_urlpatterns = [
    re_path(r'wss/sensores/$', SensorDataConsumer.as_asgi()),
]
