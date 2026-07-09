from .models import EmpresaOFundo

from .models import CustomUser


def empresa_info(request):
    empresa = None
    if request.user.is_authenticated:
        empresa = request.user.empresa
    return {'empresa': empresa}


def notificaciones_context(request):
    if request.user.is_authenticated:
        no_leidas = request.user.notificaciones.filter(leida=False).count()
    else:
        no_leidas = 0
    return {"notificaciones_no_leidas": no_leidas}
# agrosmartiot/context_processors.py
from django.conf import settings

def vapid_key(request):
    return {'VAPID_PUBLIC_KEY': settings.WEBPUSH_SETTINGS.get('VAPID_PUBLIC_KEY', '')}

