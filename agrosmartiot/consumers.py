
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import datetime

from datetime import datetime, timezone

class SensorConsumer(AsyncWebsocketConsumer):
    group_name = "sensores"  # ✅ siempre existe

    async def connect(self):
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        sensor_id = data.get("sensor_id")
        humiditysoil = data.get("humiditysoil")
        temperature = data.get("temperature")
        timestamp = datetime.now()
        # UTC
        fecha_registro = datetime.now(timezone.utc).isoformat() # Local legible

        # ✅ validar antes de guardar
        if humiditysoil is not None and temperature is not None:
            await self.save_to_db(sensor_id, humiditysoil, temperature, timestamp)

        # enviar a todos los clientes
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "sensor_data",
                "sensor_id": sensor_id,
                "humiditysoil": humiditysoil,
                "temperature": temperature,
                "timestamp": timestamp.isoformat(),
           
            }
        )

    @database_sync_to_async
    def save_to_db(self, sensor_id, humiditysoil, temperature, timestamp):
        from agrosmartiotweb.models import HumidityTemperaturaSoil
        HumidityTemperaturaSoil.objects.create(
            sensor_id=sensor_id,
            humiditysoil=humiditysoil,
            temperature=temperature,
            timestamp=timestamp,

        )

    async def sensor_data(self, event):
        await self.send(text_data=json.dumps(event))




class SensorConsumer_Aire(AsyncWebsocketConsumer):
    group_name = "sensoresaire"  # ✅ grupo siempre fijo

    async def connect(self):
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)

        sensor_id = data.get("sensor_id")
        humidity = data.get("humidity")
        temperature = data.get("temperature")
        latitude = data.get("latitude")
        longitude = data.get("longitude")

        # ✅ hora en UTC
        timestamp = datetime.now(timezone.utc)

        # Guardar en BD solo si hay datos válidos
        if humidity is not None and temperature is not None:
            await self.save_to_db(
                sensor_id,
                humidity,
                temperature,
                latitude,
                longitude,
                timestamp
            )

        # Enviar datos a todos los clientes conectados
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "sensor_data",
                "sensor_id": sensor_id,
                "humidity": humidity,
                "temperature": temperature,
                "latitude": latitude,
                "longitude": longitude,
                "timestamp": timestamp.isoformat(),
            }
        )

    @database_sync_to_async
    def save_to_db(self, sensor_id, humidity, temperature, latitude, longitude, timestamp):
        from agrosmartiotweb.models import TemperatureHumidityLocation
        TemperatureHumidityLocation.objects.create(
            sensor_id=sensor_id,
            humidity=humidity,
            temperature=temperature,
            latitude=latitude,
            longitude=longitude,
            timestamp=timestamp,
        )

    async def sensor_data(self, event):
        await self.send(text_data=json.dumps(event))