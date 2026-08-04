# chatbot/tools_clima.py

import json
import requests
from django.conf import settings
from agrosmartiotweb.models import Sector

OPENWEATHER_URL_ACTUAL = "https://api.openweathermap.org/data/2.5/weather"
OPENWEATHER_URL_FORECAST = "https://api.openweathermap.org/data/2.5/forecast"


def _centroide_sector(sector):
    """Calcula el punto promedio (centroide) del polígono guardado en Sector.coordenadas."""
    try:
        puntos = json.loads(sector.coordenadas)
        if not puntos:
            return None
        lat_prom = sum(p["lat"] for p in puntos) / len(puntos)
        lng_prom = sum(p["lng"] for p in puntos) / len(puntos)
        return lat_prom, lng_prom
    except (json.JSONDecodeError, KeyError, TypeError, ZeroDivisionError):
        return None


def _buscar_sector(user, sector_nombre):
    return Sector.objects.filter(user=user, nombre__icontains=sector_nombre).first()


def tool_clima_actual(user, sector_nombre):
    """Obtiene el clima actual (temperatura, humedad, condición) para un sector, según su ubicación real."""
    sector = _buscar_sector(user, sector_nombre)
    if not sector:
        return {"mensaje": f"No se encontró un sector llamado '{sector_nombre}'."}

    coords = _centroide_sector(sector)
    if not coords:
        return {"mensaje": f"El sector '{sector.nombre}' no tiene coordenadas válidas registradas."}

    lat, lng = coords
    try:
        response = requests.get(OPENWEATHER_URL_ACTUAL, params={
            "lat": lat, "lon": lng, "units": "metric", "lang": "es",
            "appid": settings.OPENWEATHER_API_KEY,
        }, timeout=8)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        return {"mensaje": "No se pudo obtener el clima en este momento, intenta más tarde."}

    return {
        "sector": sector.nombre,
        "temperatura": round(data["main"]["temp"], 1),
        "sensacion_termica": round(data["main"]["feels_like"], 1),
        "descripcion": data["weather"][0]["description"],
        "humedad": data["main"]["humidity"],
        "viento_ms": data["wind"]["speed"],
        "nubosidad": data["clouds"]["all"],
    }


def tool_clima_pronostico(user, sector_nombre):
    """Obtiene el pronóstico de los próximos días (temperatura y probabilidad de lluvia) para un sector."""
    sector = _buscar_sector(user, sector_nombre)
    if not sector:
        return {"mensaje": f"No se encontró un sector llamado '{sector_nombre}'."}

    coords = _centroide_sector(sector)
    if not coords:
        return {"mensaje": f"El sector '{sector.nombre}' no tiene coordenadas válidas registradas."}

    lat, lng = coords
    try:
        response = requests.get(OPENWEATHER_URL_FORECAST, params={
            "lat": lat, "lon": lng, "units": "metric", "lang": "es",
            "appid": settings.OPENWEATHER_API_KEY,
        }, timeout=8)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        return {"mensaje": "No se pudo obtener el pronóstico en este momento, intenta más tarde."}

    # La API gratuita da bloques de 3 horas por 5 días -> los agrupamos por día
    dias = {}
    for bloque in data["list"]:
        fecha = bloque["dt_txt"].split(" ")[0]  # 'YYYY-MM-DD'
        dias.setdefault(fecha, {"temps": [], "lluvia_mm": 0, "descripciones": []})
        dias[fecha]["temps"].append(bloque["main"]["temp"])
        dias[fecha]["lluvia_mm"] += bloque.get("rain", {}).get("3h", 0)
        dias[fecha]["descripciones"].append(bloque["weather"][0]["description"])

    resumen = []
    for fecha, info in dias.items():
        resumen.append({
            "fecha": fecha,
            "temp_min": round(min(info["temps"]), 1),
            "temp_max": round(max(info["temps"]), 1),
            "lluvia_estimada_mm": round(info["lluvia_mm"], 1),
            "condicion_predominante": max(set(info["descripciones"]), key=info["descripciones"].count),
        })

    return {
        "sector": sector.nombre,
        "pronostico": resumen,
        "nota": "OpenWeather gratuito entrega hasta 5 días de pronóstico, no 7.",
    }