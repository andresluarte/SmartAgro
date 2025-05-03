import json
from channels.generic.websocket import AsyncWebsocketConsumer

class SensorDataConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(text_data=json.dumps({
            'message': 'Conexión WebSocket establecida con SmartAgro'
        }))

    async def disconnect(self, close_code):
        print("WebSocket desconectado")

    async def receive(self, text_data):
        print("Mensaje recibido desde frontend:", text_data)
        await self.send(text_data=json.dumps({
            'message': 'Mensaje recibido correctamente en el servidor'
        }))



