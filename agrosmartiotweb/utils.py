# agrosmart/utils.py

from firebase_admin import messaging
from .models import Notificacion


def notificar_usuario(usuario, mensaje, titulo="SmartAgro-IoT", tipo_sensor=None, sensor_aire=None, sensor_suelo=None):
    """
    Crea una notificación en la base de datos (para la campanita)
    y, si el usuario tiene un token FCM guardado, intenta enviar
    también una notificación push real al navegador/celular.
    """

    # 1. Guardar SIEMPRE en la base de datos
    notif = Notificacion.objects.create(
        usuario=usuario,
        mensaje=mensaje,
        tipo_sensor=tipo_sensor,
        sensor_aire=sensor_aire,
        sensor_suelo=sensor_suelo,
    )

    # 2. Intentar enviar push real vía Firebase, si el usuario tiene token
    token = getattr(usuario, 'fcm_token', None)

    if token:
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
            print(f"✅ Push enviado a {usuario}")

        except messaging.UnregisteredError:
            print(f"⚠️ Token inválido para {usuario}, limpiando...")
            usuario.fcm_token = None
            usuario.save(update_fields=['fcm_token'])

        except Exception as e:
            print(f"⚠️ Error enviando push a {usuario}: {e}")

    return notif