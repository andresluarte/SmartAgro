from django.apps import AppConfig


# agrosmart/apps.py
from django.apps import AppConfig

class AgrosmartConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'agrosmartiotweb'

    def ready(self):
        from . import firebase_init  # esto ejecuta el código de inicialización
# settings.py
import os

WEBPUSH_SETTINGS = {
    'VAPID_PUBLIC_KEY': os.environ.get('VAPID_PUBLIC_KEY'),
}