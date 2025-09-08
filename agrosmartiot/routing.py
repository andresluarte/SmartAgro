# agrosmartiot/routing.py

from django.urls import re_path
from agrosmartiot.consumers import SensorConsumer,SensorConsumer_Aire

websocket_urlpatterns = [
    re_path(r"ws/sensores/$", SensorConsumer.as_asgi()),
    re_path(r"ws/sensoresaire/$", SensorConsumer_Aire.as_asgi()),
]
