# chatbot/tools_sensores.py

import re
from datetime import timedelta, datetime
from django.utils import timezone
from agrosmartiotweb.models import (
    SensorAire, SensorSuelo,
    TemperatureHumidityLocation, HumidityTemperaturaSoil,
)


def tool_ultima_lectura_aire(user, sector_nombre=None):
    """Devuelve la última lectura de temperatura/humedad de aire, opcionalmente filtrada por sector."""
    sensores = SensorAire.objects.filter(user=user)
    if sector_nombre:
        sensores = sensores.filter(sector__nombre__icontains=sector_nombre)

    resultados = []
    for sensor in sensores:
        ultima = TemperatureHumidityLocation.objects.filter(sensor=sensor).order_by('-timestamp').first()
        if ultima:
            resultados.append({
                "sensor": sensor.name,
                "sector": sensor.sector.nombre if sensor.sector else "sin sector asignado",
                "temperatura": ultima.temperature,
                "humedad": ultima.humidity,
                "hace": _tiempo_transcurrido(ultima.timestamp),
            })
    if not resultados:
        return {"mensaje": "No se encontraron lecturas de sensores de aire para ese filtro."}
    return resultados


def tool_ultima_lectura_suelo(user, sector_nombre=None):
    """Devuelve la última lectura de humedad/temperatura de suelo, opcionalmente filtrada por sector."""
    sensores = SensorSuelo.objects.filter(user=user)
    if sector_nombre:
        sensores = sensores.filter(sector__nombre__icontains=sector_nombre)

    resultados = []
    for sensor in sensores:
        ultima = HumidityTemperaturaSoil.objects.filter(sensor=sensor).order_by('-timestamp').first()
        if ultima:
            resultados.append({
                "sensor": sensor.name,
                "sector": sensor.sector.nombre if sensor.sector else "sin sector asignado",
                "humedad_suelo": ultima.humiditysoil,
                "temperatura": ultima.temperature,
                "hace": _tiempo_transcurrido(ultima.timestamp),
            })
    if not resultados:
        return {"mensaje": "No se encontraron lecturas de sensores de suelo para ese filtro."}
    return resultados


def tool_tendencia_humedad_suelo(user, sector_nombre, horas=72):
    """Calcula la tendencia (subiendo/bajando/estable) de humedad de suelo en las últimas N horas."""
    desde = timezone.now() - timedelta(hours=horas)
    sensores = SensorSuelo.objects.filter(user=user, sector__nombre__icontains=sector_nombre)

    lecturas = HumidityTemperaturaSoil.objects.filter(
        sensor__in=sensores, timestamp__gte=desde
    ).order_by('timestamp')

    if lecturas.count() < 2:
        return {"mensaje": "No hay suficientes datos históricos para calcular una tendencia."}

    primera = lecturas.first().humiditysoil
    ultima = lecturas.last().humiditysoil
    diferencia = ultima - primera

    if diferencia < -5:
        tendencia = "bajando"
    elif diferencia > 5:
        tendencia = "subiendo"
    else:
        tendencia = "estable"

    return {
        "sector": sector_nombre,
        "tendencia": tendencia,
        "humedad_hace_72h": primera,
        "humedad_actual": ultima,
        "cambio": round(diferencia, 1),
    }


def tool_sensores_sin_datos_recientes(user, horas=6):
    """Lista sensores que no han enviado datos en las últimas N horas (posible falla o desconexión)."""
    limite = timezone.now() - timedelta(hours=horas)
    alertas = []

    for sensor in SensorAire.objects.filter(user=user):
        ultima = TemperatureHumidityLocation.objects.filter(sensor=sensor).order_by('-timestamp').first()
        if not ultima or ultima.timestamp < limite:
            alertas.append({"sensor": sensor.name, "tipo": "aire", "sector": sensor.sector.nombre if sensor.sector else None})

    for sensor in SensorSuelo.objects.filter(user=user):
        ultima = HumidityTemperaturaSoil.objects.filter(sensor=sensor).order_by('-timestamp').first()
        if not ultima or ultima.timestamp < limite:
            alertas.append({"sensor": sensor.name, "tipo": "suelo", "sector": sensor.sector.nombre if sensor.sector else None})

    return alertas if alertas else {"mensaje": "Todos los sensores están reportando datos recientes."}


def _tiempo_transcurrido(timestamp):
    delta = timezone.now() - timestamp
    minutos = int(delta.total_seconds() / 60)
    if minutos < 60:
        return f"{minutos} minutos"
    horas = minutos // 60
    if horas < 24:
        return f"{horas} horas"
    return f"{horas // 24} días"


# ==================== HISTÓRICOS ====================

def _normalizar(texto):
    """Quita espacios, guiones y mayúsculas para comparar nombres de forma flexible.
    'Nodo-AIRE-01' y 'nodo aire 01' se vuelven ambos 'nodoaire01'."""
    return re.sub(r'[\s\-_]+', '', texto).lower()


def _buscar_sensor_aire(user, sensor_nombre):
    """Busca un sensor de aire comparando nombres normalizados, no substring literal."""
    objetivo = _normalizar(sensor_nombre)
    for sensor in SensorAire.objects.filter(user=user):
        if objetivo in _normalizar(sensor.name):
            return sensor
    return None


def _buscar_sensor_suelo(user, sensor_nombre):
    """Busca un sensor de suelo comparando nombres normalizados, no substring literal."""
    objetivo = _normalizar(sensor_nombre)
    for sensor in SensorSuelo.objects.filter(user=user):
        if objetivo in _normalizar(sensor.name):
            return sensor
    return None


def tool_historico_aire(user, sensor_nombre, fecha_inicio, fecha_fin):
    """Devuelve un resumen de las lecturas de un sensor de aire específico entre dos fechas."""
    sensor = _buscar_sensor_aire(user, sensor_nombre)
    if not sensor:
        return {"mensaje": f"No se encontró un sensor de aire llamado '{sensor_nombre}'."}

    inicio = _parsear_fecha(fecha_inicio)
    fin = _parsear_fecha(fecha_fin, fin_del_dia=True)
    if not inicio or not fin:
        return {"mensaje": "No pude interpretar las fechas, usa formato YYYY-MM-DD."}

    lecturas = TemperatureHumidityLocation.objects.filter(
        sensor=sensor, timestamp__gte=inicio, timestamp__lte=fin
    ).order_by('timestamp')

    if not lecturas.exists():
        return {"mensaje": f"No hay lecturas de '{sensor.name}' entre {fecha_inicio} y {fecha_fin}."}

    return _resumir_lecturas_aire(sensor.name, lecturas)


def tool_historico_suelo(user, sensor_nombre, fecha_inicio, fecha_fin):
    """Devuelve un resumen de las lecturas de un sensor de suelo específico entre dos fechas."""
    sensor = _buscar_sensor_suelo(user, sensor_nombre)
    if not sensor:
        return {"mensaje": f"No se encontró un sensor de suelo llamado '{sensor_nombre}'."}

    inicio = _parsear_fecha(fecha_inicio)
    fin = _parsear_fecha(fecha_fin, fin_del_dia=True)
    if not inicio or not fin:
        return {"mensaje": "No pude interpretar las fechas, usa formato YYYY-MM-DD."}

    lecturas = HumidityTemperaturaSoil.objects.filter(
        sensor=sensor, timestamp__gte=inicio, timestamp__lte=fin
    ).order_by('timestamp')

    if not lecturas.exists():
        return {"mensaje": f"No hay lecturas de '{sensor.name}' entre {fecha_inicio} y {fecha_fin}."}

    return _resumir_lecturas_suelo(sensor.name, lecturas)


def _parsear_fecha(fecha_str, fin_del_dia=False):
    """Convierte 'YYYY-MM-DD' a datetime timezone-aware, al inicio o fin del día."""
    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
        if fin_del_dia:
            fecha = fecha.replace(hour=23, minute=59, second=59)
        return timezone.make_aware(fecha)
    except (ValueError, TypeError):
        return None


def _resumir_lecturas_aire(nombre_sensor, lecturas):
    """No manda cada lectura individual a Claude (serían cientos) — manda un resumen estadístico."""
    valores_temp = [l.temperature for l in lecturas]
    valores_hum = [l.humidity for l in lecturas]

    return {
        "sensor": nombre_sensor,
        "cantidad_lecturas": lecturas.count(),
        "desde": lecturas.first().timestamp.strftime("%Y-%m-%d %H:%M"),
        "hasta": lecturas.last().timestamp.strftime("%Y-%m-%d %H:%M"),
        "temperatura_promedio": round(sum(valores_temp) / len(valores_temp), 1),
        "temperatura_maxima": round(max(valores_temp), 1),
        "temperatura_minima": round(min(valores_temp), 1),
        "humedad_promedio": round(sum(valores_hum) / len(valores_hum), 1),
        "humedad_maxima": round(max(valores_hum), 1),
        "humedad_minima": round(min(valores_hum), 1),
    }


def _resumir_lecturas_suelo(nombre_sensor, lecturas):
    valores_hum = [l.humiditysoil for l in lecturas]
    valores_temp = [l.temperature for l in lecturas]

    return {
        "sensor": nombre_sensor,
        "cantidad_lecturas": lecturas.count(),
        "desde": lecturas.first().timestamp.strftime("%Y-%m-%d %H:%M"),
        "hasta": lecturas.last().timestamp.strftime("%Y-%m-%d %H:%M"),
        "humedad_suelo_promedio": round(sum(valores_hum) / len(valores_hum), 1),
        "humedad_suelo_maxima": round(max(valores_hum), 1),
        "humedad_suelo_minima": round(min(valores_hum), 1),
        "temperatura_promedio": round(sum(valores_temp) / len(valores_temp), 1),
    }