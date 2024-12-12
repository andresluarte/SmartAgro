from rest_framework import serializers
from .models import Procesos

class ProcesoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Procesos
        fields = (
            'trabajo_nombre',
            'estado',
    
            'huerto_nombre',
            'asignado',
        )



from .models import TemperatureHumidityLocation

class TemperatureHumidityLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemperatureHumidityLocation
        fields = ('temperature', 'humidity', 'latitude', 'longitude')
