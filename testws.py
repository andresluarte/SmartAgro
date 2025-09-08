import asyncio
import websockets
import json
import datetime

async def test():
    uri = "ws://127.0.0.1:8000/ws/sensoresaire/"  # tu endpoint WebSocket
    async with websockets.connect(uri) as websocket:
        # Crear un mensaje simulado
        data = {
            "type": "sensor_data",
            "sensor_id": 2,          # id del sensor
            "humidity":28
            ,      # porcentaje de humedad
            "temperature": 30,     # temperatura en °C
            "latitude": -38.7369,    # valor de ejemplo
            "longitude": -72.5901,   # valor de ejemplo
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "fecha_registro": datetime.datetime.utcnow().isoformat()
        }

        # Enviar el mensaje
        await websocket.send(json.dumps(data))
        print(f"📤 Enviado: {data}")

        # Esperar respuesta del servidor (si tu WS devuelve algo)
        try:
            response = await websocket.recv()
            print(f"📥 Respuesta: {response}")
        except websockets.exceptions.ConnectionClosedOK:
            print("Conexión cerrada por el servidor")

# Ejecutar la función
asyncio.run(test())
