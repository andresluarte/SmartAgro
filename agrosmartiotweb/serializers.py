from rest_framework import serializers
from .models import Procesos

class ProcesoSerializer(serializers.ModelSerializer):
    sector_nombre = serializers.CharField(source="sector.nombre")
    lote_nombre = serializers.CharField(source="lote.nombre")
    huerto_nombre = serializers.CharField(source="huerto.nombre")
    class Meta:
        model = Procesos
        fields = (
            'trabajo',
            'estado',
            'sector_nombre',
            'lote_nombre',
            'huerto_nombre',
            'asignado',
        )



from .models import TemperatureHumidityLocation

class TemperatureHumidityLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemperatureHumidityLocation
        fields = ('temperature', 'humidity', 'latitude', 'longitude')
