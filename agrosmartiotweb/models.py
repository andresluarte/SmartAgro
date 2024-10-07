# models.py

from django.conf import settings  # Importa settings
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
import re
from django.core.exceptions import ValidationError
import datetime
import requests
import json
# Validador de RUT chileno
def validate_rut(value):
    rut_pattern = r'^\d{1,8}-[\dKk]$'
    if not re.match(rut_pattern, value):
        raise ValidationError('El formato del RUT no es válido')

class Sector(models.Model):
    nombre = models.CharField(max_length=50)
    coordenadas = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sector_creado', on_delete=models.CASCADE)


    def __str__(self):
        return self.nombre
    
  # If using PostgreSQL

class SectorPoligon(models.Model):
    nombre = models.CharField(max_length=100)
    coordenadas = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Relación con el usuario  # Almacenaremos las coordenadas como un JSON (array de objetos LatLng)  # For Django 3.1+, JSONField is available by default
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='sectorPoligon_creado', on_delete=models.CASCADE
    )
    def __str__(self):
        return self.nombre



    

class Huerto(MPTTModel):
    nombre = models.CharField(max_length=50)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='lotes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Actualiza aquí
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='huerto_creado', on_delete=models.CASCADE)

    class MPTTMeta:
        order_insertion_by = ['nombre']

    def __str__(self):
        return self.nombre

class Lote(models.Model):
    nombre = models.CharField(max_length=50)
    huerto = models.ForeignKey(Huerto, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Actualiza aquí
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='lote_creado', on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

class SensorData(models.Model):
    temperature = models.FloatField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Actualiza aquí
    
    def __str__(self):
        return self.temperature

class Trabajador(models.Model):
    foto = models.ImageField(upload_to='fundos/fotosnueva/', null=True, blank=True)# Campo de imagen opcional
    nombre = models.CharField(max_length=50, null=True)
    rut = models.CharField(max_length=12, null=True, validators=[validate_rut])
    TIPO_CONTRATO_CHOICES = (
        ('Indefinido', 'Indefinido'),
        ('Plazo fijo', 'Plazo fijo'),
        ('Honorario', 'Honorario'),
        ('Sin Contrato', 'Sin Contrato'),
    )
    fecha_ingreso = models.DateField(default=datetime.date.today)
    fecha_termino_contrato = models.DateField(blank=True, null=True)
    tipo_contraro = models.CharField(max_length=15, choices=TIPO_CONTRATO_CHOICES, default="Plazo fijo", editable=True)
    cobro = models.IntegerField(blank=True, null=True)
    trabajo_a_realizar = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Usuario al que pertenece el trabajador
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='trabajadores_creados', on_delete=models.CASCADE)  # Admin que creó al trabajador

    def __str__(self):
        return self.nombre

    @property
    def cantidad_tareas(self):
        return self.procesos_set.count()

    def cantidad_jornada(self):
        # Contar las jornadas de tipo Jornada y JornadaPorTrato
        total_jornadas = self.jornada_set.count() + self.jornadaportrato_set.count()
        return total_jornadas

    class Meta:
        ordering = ['-fecha_ingreso']

class Procesos(models.Model):
    trabajo = models.CharField(max_length=50, null=True, blank=True)
    fecha = models.DateField(default=datetime.date.today)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, max_length=50, null=True, default="sin especificar", blank=True)
    huerto = models.ForeignKey(Huerto, on_delete=models.CASCADE, max_length=50, null=True, default="sin especificar", blank=True)
    lote = models.ForeignKey(Lote, on_delete=models.CASCADE, max_length=50, null=True, default="sin especificar", blank=True)
    ESTADO_CHOICES = (
        ('Por Realizar', 'Por Realizar'),
        ('En Proceso', 'En Proceso'),
        ('Terminado', 'Terminado'),
    )
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='Por Realizar', editable=True)
    asignado = models.ForeignKey(Trabajador, on_delete=models.CASCADE, max_length=50, null=True)
    hora_asignada = models.TimeField(null=True)
    hora_creacion = models.TimeField(default=datetime.datetime.now().time(), editable=False)
    presupuesto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    observacion = models.CharField(max_length=100, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Actualiza aquí
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='procesos_creados', on_delete=models.CASCADE)
    def __str__(self):
        return self.trabajo

class Contacto(models.Model):
    nombre = models.CharField(max_length=50)
    correo = models.EmailField()
    OPCIONES_CONSULTAS = [
        [0, "Consulta"],
        [1, "Reclamo"],
        [2, "Sugerencia"],
        [3, "Felicitaciones"]
    ]
    tipo_consulta = models.IntegerField(choices=OPCIONES_CONSULTAS)
    mensaje = models.TextField()
    avisos = models.BooleanField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Actualiza aquí

    def __str__(self):
        return self.nombre

class Jornada(models.Model):
    fecha_creacion = models.DateField(default=datetime.date.today, editable=False)
    hora_creacion = models.TimeField(default=datetime.datetime.now().time(), editable=False)
    asignado = models.ForeignKey(Trabajador, on_delete=models.CASCADE, max_length=50, null=True)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, max_length=50, null=True, blank=True)
    huerto = models.ForeignKey(Huerto, on_delete=models.CASCADE, max_length=50, null=True, blank=True)
    lote = models.ForeignKey(Lote, on_delete=models.CASCADE, max_length=50, null=True, blank=True)
    fecha = models.DateField()
    ESTADO_CHOICES = (
        ('Por Realizar', 'Por Realizar'),
        ('En Proceso', 'En Proceso'),
        ('Terminado', 'Terminado'),
    )
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='Por Realizar', editable=True)
    es_jornada_por_trato = models.BooleanField(default=False) 
    nombre_tarea_1 = models.CharField(max_length=100)
    hora_inicio_tarea_1 = models.TimeField()
    hora_fin_tarea_1 = models.TimeField()
    cobro_tarea_1 = models.IntegerField(blank=True, null=True)
    nombre_tarea_2 = models.CharField(max_length=100, blank=True, null=True)
    hora_inicio_tarea_2 = models.TimeField(blank=True, null=True)
    hora_fin_tarea_2 = models.TimeField(blank=True, null=True)
    cobro_tarea_2 = models.IntegerField(blank=True, null=True)
    nombre_tarea_3 = models.CharField(max_length=100, blank=True, null=True)
    hora_inicio_tarea_3 = models.TimeField(blank=True, null=True)
    hora_fin_tarea_3 = models.TimeField(blank=True, null=True)
    cobro_tarea_3 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    nombre_extra_1 = models.CharField(max_length=100, blank=True, null=True)
    gasto_extra_1 = models.IntegerField(blank=True, null=True)
    nombre_extra_2 = models.CharField(max_length=100, blank=True, null=True)
    gasto_extra_2 = models.IntegerField(blank=True, null=True)
    nombre_extra_3 = models.CharField(max_length=100, blank=True, null=True)
    gasto_extra_3 = models.IntegerField(blank=True, null=True)
    observacion = models.CharField(max_length=200, null=True, blank=True)
    total_gasto_jornada = models.IntegerField(blank=True, null=True, editable=False)
    detalle_gasto_total_tareas = models.IntegerField(blank=True, null=True, editable=False)
    detalle_gastos_total_extras = models.IntegerField(blank=True, null=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Usuario que creó la jornada
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='jornadas_creadas', on_delete=models.CASCADE)  # Usuario que creó la jornada

    class Meta:
        ordering = ['-fecha_creacion', '-hora_creacion']

    def __str__(self):
        return f"Jornada {self.fecha} {self.hora_creacion}"

    @property
    def total_gasto_jornada_calculado(self):
        total_gasto = (self.cobro_tarea_1 or 0) + (self.cobro_tarea_2 or 0) + (self.cobro_tarea_3 or 0) + (self.gasto_extra_1 or 0) + (self.gasto_extra_2 or 0) + (self.gasto_extra_3 or 0)
        return total_gasto




from django.db import models
from django.conf import settings
from datetime import date, time
from agrosmartiotweb.models import Trabajador, Sector, Huerto, Lote




from django.db import models
from django.conf import settings
import datetime

class JornadaPorTrato(models.Model):
    fecha_creacion = models.DateField(default=datetime.date.today, editable=False)
    hora_creacion = models.TimeField(default=datetime.datetime.now().time(), editable=False)
    asignado = models.ForeignKey('Trabajador', on_delete=models.CASCADE, max_length=50, null=True)
    sector = models.ForeignKey('Sector', on_delete=models.CASCADE, max_length=50, null=True, blank=True)
    huerto = models.ForeignKey('Huerto', on_delete=models.CASCADE, max_length=50, null=True, blank=True)
    lote = models.ForeignKey('Lote', on_delete=models.CASCADE, max_length=50, null=True, blank=True)
    fecha = models.DateField()
    
    ESTADO_CHOICES = (
        ('Por Realizar', 'Por Realizar'),
        ('En Proceso', 'En Proceso'),
        ('Terminado', 'Terminado'),
    )
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='Por Realizar', editable=True)
    
    # Tareas
    nombre_tarea_1 = models.CharField(max_length=100)
    cobro_tarea_1 = models.IntegerField(blank=True, null=True)
    
    nombre_tarea_2 = models.CharField(max_length=100, blank=True, null=True)
    cobro_tarea_2 = models.IntegerField(blank=True, null=True)
    
    nombre_tarea_3 = models.CharField(max_length=100, blank=True, null=True)
    cobro_tarea_3 = models.IntegerField(blank=True, null=True)
    
    # Extras
    nombre_extra_1 = models.CharField(max_length=100, blank=True, null=True)
    gasto_extra_1 = models.IntegerField(blank=True, null=True)
    
    nombre_extra_2 = models.CharField(max_length=100, blank=True, null=True)
    gasto_extra_2 = models.IntegerField(blank=True, null=True)
    
    nombre_extra_3 = models.CharField(max_length=100, blank=True, null=True)
    gasto_extra_3 = models.IntegerField(blank=True, null=True)
    
    observacion = models.CharField(max_length=200, null=True, blank=True)
    # Detalles del gasto
    detalle_gasto_total_tareas = models.IntegerField(blank=True, null=True, editable=False)
    detalle_gastos_total_extras = models.IntegerField(blank=True, null=True, editable=False)
    total_gasto_jornada = models.IntegerField(blank=True, null=True, editable=False)
    
    # Relación con usuarios
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='jornadas_por_trato_creadas', on_delete=models.CASCADE)

    class Meta:
        ordering = ['-fecha_creacion', '-hora_creacion']

    def __str__(self):
        return f"JornadaPorTrato {self.fecha} {self.hora_creacion}"

    @property
    def total_gasto_jornada_calculado(self):
        # Sumar cobros y gastos para obtener el total
        total_gasto_tareas = (self.cobro_tarea_1 or 0) + (self.cobro_tarea_2 or 0) + (self.cobro_tarea_3 or 0)
        total_gastos_extras = (self.gasto_extra_1 or 0) + (self.gasto_extra_2 or 0) + (self.gasto_extra_3 or 0)
        return total_gasto_tareas + total_gastos_extras


from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('superuser', 'Superusuario'),
        ('admin', 'Administrador'),
        ('colaborador', 'Colaborador'),
        ('ayudante', 'Ayudante'),
        ('agricultor', 'Agricultor'),
    )
    user_type = models.CharField(max_length=15, choices=USER_TYPE_CHOICES, default='superuser')
    created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_users')
    empresa = models.ForeignKey('EmpresaOFundo', on_delete=models.SET_NULL, null=True, blank=True, related_name='empresas')

    def __str__(self):
        return self.username

    # Define un related_name para evitar conflictos con el modelo User por defecto
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    def __str__(self):
        return self.username



class EmpresaOFundo(models.Model):
    nombre = models.CharField(max_length=255)
    numero_hectareas = models.DecimalField(max_digits=10, decimal_places=2)
    foto1 = models.ImageField(upload_to='fundos/fotos/', null=True, blank=True)
    foto2 = models.ImageField(upload_to='fundos/fotos/', null=True, blank=True)
    foto3 = models.ImageField(upload_to='fundos/fotos/', null=True, blank=True)
    logo = models.ImageField(upload_to='fundos/logos/', null=True, blank=True)
    ubicacion = models.CharField(max_length=255, null=True, blank=True)
    tipo_cultivo = models.CharField(max_length=255, null=True, blank=True)
    # Relación con usuarios
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) 
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='empresa_creada', on_delete=models.CASCADE)
    
    # Otros campos que consideres importantes
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nombre


#MODELOS DE SENSOR 

class TemperatureHumidityLocation(models.Model):
    temperature = models.FloatField()
    humidity = models.FloatField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Temperature: {self.temperature}, Humidity: {self.humidity}, Latitude: {self.latitude}, Longitude: {self.longitude}"

class HumiditySoil(models.Model):
    humiditysoil = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Humidity: {self.humiditysoil}, Timestamp: {self.timestamp}"
    
from django.db.models import Sum

#finanzas por trabajador
class FinanzasPorTrabajador(models.Model):
    trabajador = models.ForeignKey(Trabajador, on_delete=models.CASCADE)
    total_gasto_jornadas = models.IntegerField(default=0, editable=False)  # Total de todas las jornadas
    total_gasto_jornadas_por_trato = models.IntegerField(default=0, editable=False)  # Total de todas las jornadas por trato
    total_gasto_final = models.IntegerField(default=0, editable=False)  # Suma de ambos totales
 
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='finanzas_creadas', on_delete=models.CASCADE)  # Admin que gestionó las finanzas
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Usuario que está visualizando

    def actualizar_finanzas_trabajador(trabajador, creador):
        # Obtener o crear el registro de finanzas para el trabajador
        finanzas, created = FinanzasPorTrabajador.objects.get_or_create(
            trabajador=trabajador,
            created_by=creador,
            defaults={'user': creador}
        )

        # Calcular total de gastos por jornadas normales y jornadas por trato
        total_jornadas = Jornada.objects.filter(asignado=trabajador).aggregate(total=Sum('total_gasto_jornada'))['total'] or 0
        total_jornadas_por_trato = JornadaPorTrato.objects.filter(asignado=trabajador).aggregate(total=Sum('total_gasto_jornada'))['total'] or 0

        # Actualizar los campos del modelo FinanzasPorTrabajador
        finanzas.total_gasto_jornadas = total_jornadas
        finanzas.total_gasto_jornadas_por_trato = total_jornadas_por_trato
        finanzas.total_gasto_final = total_jornadas + total_jornadas_por_trato

        finanzas.save()






    