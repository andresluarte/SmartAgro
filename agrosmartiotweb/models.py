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

from django.db import models
from django.conf import settings

from django.db import models

class InsumoOpciones(models.Model):
    OPCIONES_TRABAJO = [
        ("Fertilizantes (urea, nitrato de amonio)", "Fertilizantes (urea, nitrato de amonio)"),
        ("Fungicidas (azufre, Tercel 50 WP)", "Fungicidas (azufre, Tercel 50 WP)"),
        ("Herbicidas (Roundup)", "Herbicidas (Roundup)"),
        ("Pesticidas (Podexal)", "Pesticidas (Podexal)"),
        ("Agua de riego", "Agua de riego"),
        ("Postes y alambres", "Postes y alambres"),
        ("Cintas de amarre", "Cintas de amarre"),
        ("Semillas", "Semillas"),
        ("Sustratos", "Sustratos"),
        ("Aplicación de pesticidas y fertilizantes", "Aplicación de pesticidas y fertilizantes"),
        ("Tractores, arados, sembradoras", "Tractores, arados, sembradoras"),
        ("Sistema de riego", "Sistema de riego"),
        ("Pulverizadores", "Pulverizadores"),
        ("Transporte de insumos", "Transporte de insumos"),
        ("Cosecha y acarreo de uvas", "Cosecha y acarreo de uvas"),
        ("Otro", "Otro"),
    ]

    opciones_trabajo = models.CharField(max_length=100, choices=OPCIONES_TRABAJO)

    def __str__(self):
        return self.opciones_trabajo





class Procesos(models.Model):
    trabajo = models.ForeignKey(InsumoOpciones, on_delete=models.CASCADE, null=True)
    
    fecha = models.DateField(default=datetime.date.today)
    
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
        return str(self.trabajo) if self.trabajo else "Sin trabajo"
    
    

    

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
    MANODEOBRACHOICES = [
    ('PODA', 'Poda'),
    ('DESHOJE', 'Deshoje (sacar hojas)'),
    ('DESBROTE', 'Desbrote'),
    ('PESTICIDAS', 'Aplicación de pesticidas'),
    ('FERTILIZANTES', 'Aplicación de fertilizantes'),
    ('COSECHA', 'Cosecha'),
    ('AMARRE_GUIAS', 'Amarre de guías'),
    ('LIMPIEZA_MALEZA', 'Limpieza de maleza'),
    ('RIEGO', 'Riego'),
]
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

    nombre_tarea_1 = models.CharField(max_length=100,choices=MANODEOBRACHOICES)

    hora_inicio_tarea_1 = models.TimeField()

    hora_fin_tarea_1 = models.TimeField()

    cobro_tarea_1 = models.IntegerField(blank=True, null=True)

    nombre_tarea_2 = models.CharField(max_length=100,choices=MANODEOBRACHOICES,blank=True, null=True)

    hora_inicio_tarea_2 = models.TimeField(blank=True, null=True)
    
    hora_fin_tarea_2 = models.TimeField(blank=True, null=True)

    cobro_tarea_2 = models.IntegerField(blank=True, null=True)

    nombre_tarea_3 = models.CharField(max_length=100,choices=MANODEOBRACHOICES,blank=True, null=True)

    hora_inicio_tarea_3 = models.TimeField(blank=True,  null=True)

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
    MANODEOBRACHOICES = [
    ('PODA', 'Poda'),
    ('DESHOJE', 'Deshoje (sacar hojas)'),
    ('DESBROTE', 'Desbrote'),
    ('PESTICIDAS', 'Aplicación de pesticidas'),
    ('FERTILIZANTES', 'Aplicación de fertilizantes'),
    ('COSECHA', 'Cosecha'),
    ('AMARRE_GUIAS', 'Amarre de guías'),
    ('LIMPIEZA_MALEZA', 'Limpieza de maleza'),
    ('RIEGO', 'Riego'),
]

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
    nombre_tarea_1 = models.CharField(max_length=100,choices=MANODEOBRACHOICES)
    cobro_tarea_1 = models.IntegerField(blank=True, null=True)
    
    nombre_tarea_2 = models.CharField(max_length=100,choices=MANODEOBRACHOICES, blank=True, null=True)
    cobro_tarea_2 = models.IntegerField(blank=True, null=True)
    
    nombre_tarea_3 = models.CharField(max_length=100,choices=MANODEOBRACHOICES, blank=True, null=True)
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
import uuid


class SensorAire(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Nombre único para cada sensor
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    api_key = models.CharField(max_length=64, blank=True, null=True, unique=True)  # API Key única

    def save(self, *args, **kwargs):
        # Generar una API Key única si no existe
        if not self.api_key:
            self.api_key = uuid.uuid4().hex  # Generar clave única con uuid
         
        # Si no hay nombre, generarlo automáticamente
        if not self.name:
            # Garantizar que el nombre generado sea único dentro del contexto del usuario
            count = SensorAire.objects.filter(user=self.user).count() + 1
            unique_name = f"{self.user.username}_sensor_{count}"
            
            # Asegurarse de que no haya conflicto con otros nombres únicos
            while SensorAire.objects.filter(name=unique_name).exists():
                count += 1
                unique_name = f"{self.user.username}_sensor_{count}"
            
            self.name = unique_name  # Asignar el nombre generado

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sensor: {self.name} de {self.user.username}"

class SensorSuelo(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Nombre único para cada sensor
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    api_key = models.CharField(max_length=64, blank=True, null=True, unique=True)  # API Key única

    def save(self, *args, **kwargs):
        # Generar una API Key única si no existe
        if not self.api_key:
            self.api_key = uuid.uuid4().hex  # Generar clave única con uuid
         
        # Si no hay nombre, generarlo automáticamente
        if not self.name:
            # Garantizar que el nombre generado sea único dentro del contexto del usuario
            count = SensorSuelo.objects.filter(user=self.user).count() + 1
            unique_name = f"{self.user.username}_sensor_{count}"
            
            # Asegurarse de que no haya conflicto con otros nombres únicos
            while SensorSuelo.objects.filter(name=unique_name).exists():
                count += 1
                unique_name = f"{self.user.username}_sensor_{count}"
            
            self.name = unique_name  # Asignar el nombre generado

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sensor: {self.name} de {self.user.username}"


    
class TemperatureHumidityLocation(models.Model):
    temperature = models.FloatField()
    humidity = models.FloatField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    sensor = models.ForeignKey(SensorAire, on_delete=models.CASCADE)  # Asociar datos con un sensor específico

    def __str__(self):
        return f"Sensor: {self.sensor.name}, Temp: {self.temperature}, Hum: {self.humidity}, Lat: {self.latitude}, Lon: {self.longitude}"

class HumidityTemperaturaSoil(models.Model):
    humiditysoil = models.FloatField()
    temperature = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    sensor = models.ForeignKey(SensorSuelo, on_delete=models.CASCADE)  # Asociar datos con un sensor específico

    def __str__(self):        
        return f"Sensor: {self.sensor.name}, Humidity: {self.humiditysoil}, Temperature: {self.temperature}, Timestamp: {self.timestamp}"

    
class DecisionEfectuada(models.Model):
    decision = models.CharField(max_length=5000)  # Campo para la decisión
    sector = models.ForeignKey('Sector', on_delete=models.CASCADE, max_length=50)  # Clave foránea a Sector
    huerto = models.ForeignKey('Huerto', on_delete=models.CASCADE, null=True, blank=True)  # Clave foránea a Huerto
    lote = models.ForeignKey('Lote', on_delete=models.CASCADE, null=True, blank=True)  # Clave foránea a Lote
    created_at = models.DateTimeField(auto_now_add=True)  # Fecha de creación automática
    sensor = models.ForeignKey('SensorAire', on_delete=models.CASCADE, null=True, blank=True)  # Clave foránea a SensorAire
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='decisiones_tomadas', on_delete=models.CASCADE)  # Usuario que realizó la acción
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Usuario que está visualizando

    def __str__(self):
        return f"Decisión: {self.decision} - Sector: {self.sector} - Huerto: {self.huerto} - Lote: {self.lote} - Sensor: {self.sensor}"

    
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


from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal

class FinanzasPorInsumosyMaquinaria(models.Model):
    trabajo = models.ForeignKey(Procesos, on_delete=models.CASCADE, null=True, blank=True)
    gasto_total = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='finanzas_user')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='finanzas_created_by')

    def __str__(self):
        return f"Finanza de {self.trabajo}"

    @classmethod
    def total_por_trabajo(cls):
        # Agrupa los gastos totales por trabajo
        return cls.objects.values('trabajo').annotate(total_gasto=Sum('gasto_total'))

@receiver(post_save, sender=Procesos)
def crear_finanzas(sender, instance, created, **kwargs):
    if instance.estado == 'Terminado':
        # Busca o crea el registro de finanzas para el trabajo
        finanzas, created = FinanzasPorInsumosyMaquinaria.objects.get_or_create(
            trabajo=instance,
            defaults={'gasto_total': instance.presupuesto, 'user': instance.user, 'created_by': instance.created_by}
        )
        if not created:
            # Si ya existe, suma el presupuesto al gasto total existente
            finanzas.gasto_total += instance.presupuesto
            finanzas.save()


class Cosecha(models.Model):
    foto = models.ImageField(upload_to='fundos/fotosnueva/', null=True, blank=True)
    sector = models.ForeignKey('Sector', on_delete=models.CASCADE, max_length=50, null=True, blank=True)
    huerto = models.ForeignKey('Huerto', on_delete=models.CASCADE, max_length=50, null=True, blank=True)
    lote = models.ForeignKey('Lote', on_delete=models.CASCADE, max_length=50, null=True, blank=True)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)  # Cantidad cosechada en kilos u otra medida
    fecha_cosecha = models.DateField()  # Fecha en la que se realizó la cosecha
    tipo_producto = models.CharField(max_length=100)  # Tipo de producto cosechado (fruta, verdura, etc.)
    calidad = models.CharField(max_length=50, choices=[('Alta', 'Alta'), ('Media', 'Media'), ('Baja', 'Baja')], default='Media')  # Calidad de la cosecha
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='cosechas_creadas', on_delete=models.CASCADE)  # Usuario que creó el registro
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Usuario asociado a la cosecha
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # Fecha en la que se creó el registro
    ultima_modificacion = models.DateTimeField(auto_now=True)  # Fecha de la última modificación

     # Usuario que está visualizando

    class Meta:
        verbose_name = "Cosecha"
        verbose_name_plural = "Cosechas"
        ordering = ['-fecha_cosecha']

    def __str__(self):
        return f'Cosecha de {self.tipo_producto} - {self.fecha_cosecha}'

from django.db.models.functions import TruncMonth


class FinanzasPorMes(models.Model):
    mes_año = models.DateField()
    total_gasto_jornadas = models.IntegerField(blank=True, null=True, editable=False)  # Permitir nulos
    total_gasto_jornadas_por_trato = models.IntegerField(blank=True, null=True, editable=False)  # Permitir nulos
    total_gasto_final = models.IntegerField(blank=True, null=True, editable=False)  # Permitir nulos
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='finanzas_por_mes_creada', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    @classmethod
    def actualizar_finanzas_por_mes(cls, fecha, creador):
        inicio_mes = fecha.replace(day=1)

        finanzas, created = cls.objects.get_or_create(
            mes_año=inicio_mes,
            defaults={
                'total_gasto_jornadas': 0,
                'total_gasto_jornadas_por_trato': 0,
                'total_gasto_final': 0,
                'created_by': creador,
                'user': creador
            }
        )

        # Usar la agregación de Django para obtener los totales
        total_jornadas = Jornada.objects.filter(fecha__year=fecha.year, fecha__month=fecha.month).aggregate(total=Sum('total_gasto_jornada'))['total'] or 0
        total_jornadas_por_trato = JornadaPorTrato.objects.filter(fecha__year=fecha.year, fecha__month=fecha.month).aggregate(total=Sum('total_gasto_jornada'))['total'] or 0

        # Actualizar el modelo con los totales
        finanzas.total_gasto_jornadas = total_jornadas
        finanzas.total_gasto_jornadas_por_trato = total_jornadas_por_trato
        finanzas.total_gasto_final = (total_jornadas or 0) + (total_jornadas_por_trato or 0)

        finanzas.save()
