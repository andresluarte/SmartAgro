# chatbot/tools_recomendacion.py

from datetime import timedelta
from django.utils import timezone
from agrosmartiotweb.models import Sector, SensorSuelo, HumidityTemperaturaSoil

from .tools_clima import _centroide_sector, tool_clima_pronostico
from .tools_sensores import _resumir_lecturas_suelo


def tool_resumen_sector(user, sector_nombre, dias_historial=7):
    """
    Combina: histórico reciente de humedad/temperatura de suelo del sector +
    pronóstico del clima del sector, para servir de base a una recomendación.
    Úsala cuando pidan una recomendación o un panorama completo de un sector.
    """
    sector = Sector.objects.filter(user=user, nombre__icontains=sector_nombre).first()
    if not sector:
        return {"mensaje": f"No se encontró un sector llamado '{sector_nombre}'."}

    # 1. Histórico de sensores de suelo del sector (pasado)
    desde = timezone.now() - timedelta(days=dias_historial)
    sensores_suelo = SensorSuelo.objects.filter(user=user, sector=sector)

    resumen_sensores = []
    for sensor in sensores_suelo:
        lecturas = HumidityTemperaturaSoil.objects.filter(
            sensor=sensor, timestamp__gte=desde
        ).order_by('timestamp')
        if lecturas.exists():
            resumen_sensores.append(_resumir_lecturas_suelo(sensor.name, lecturas))

    # 2. Pronóstico del clima del sector (futuro)
    pronostico = tool_clima_pronostico(user, sector_nombre)

    if not resumen_sensores and "mensaje" in pronostico:
        return {"mensaje": f"No hay datos de sensores ni de clima disponibles para '{sector.nombre}'."}

    return {
        "sector": sector.nombre,
        "periodo_historico_dias": dias_historial,
        "historico_sensores_suelo": resumen_sensores if resumen_sensores else "Sin datos de sensores de suelo en este período.",
        "pronostico_clima": pronostico,
    }