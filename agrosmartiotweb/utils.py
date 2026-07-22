# agrosmart/utils.py

import threading
import logging

from firebase_admin import messaging
from .models import Notificacion

logger = logging.getLogger(__name__)


def _enviar_push_async(usuario, titulo, mensaje):
    """
    Envía el push de Firebase en un hilo aparte, para que una demora
    o falla de Firebase NUNCA bloquee el request que llamó a notificar_usuario
    (ej. el endpoint que recibe datos del sensor).
    """
    token = getattr(usuario, 'fcm_token', None)
    if not token:
        return

    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=titulo,
                body=mensaje,
            ),
            token=token,
            webpush=messaging.WebpushConfig(
                notification=messaging.WebpushNotification(
                    icon="/static/app/img/logopequeño.jpg",
                    vibrate=[100],
                )
            )
        )
        messaging.send(message)
        logger.info(f"✅ Push enviado a {usuario}")

    except messaging.UnregisteredError:
        logger.warning(f"⚠️ Token inválido para {usuario}, limpiando...")
        usuario.fcm_token = None
        usuario.save(update_fields=['fcm_token'])

    except Exception as e:
        logger.warning(f"⚠️ Error enviando push a {usuario}: {e}")


def notificar_usuario(usuario, mensaje, titulo="SmartAgro-IoT", tipo_sensor=None, sensor_aire=None, sensor_suelo=None):
    """
    Crea una notificación en la base de datos (para la campanita)
    y, si el usuario tiene un token FCM guardado, lanza el envío del
    push real en un hilo aparte para no bloquear al caller (ej. el
    endpoint de ingesta de datos del sensor).
    """

    # 1. Guardar SIEMPRE en la base de datos (esto es rápido, se queda igual)
    notif = Notificacion.objects.create(
        usuario=usuario,
        mensaje=mensaje,
        tipo_sensor=tipo_sensor,
        sensor_aire=sensor_aire,
        sensor_suelo=sensor_suelo,
    )

    # 2. El push a Firebase ya NO bloquea — corre en background
    threading.Thread(
        target=_enviar_push_async,
        args=(usuario, titulo, mensaje),
        daemon=True
    ).start()

    return notif