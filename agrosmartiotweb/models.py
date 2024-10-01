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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    google_maps_link = models.URLField(max_length=200, null=True, blank=True)  # Actualiza aquí
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sector_creado', on_delete=models.CASCADE)
    def save(self, *args, **kwargs):
        if self.google_maps_link and (not self.latitud or not self.longitud):
            lat, lng = self.extract_lat_lng_from_link(self.google_maps_link)
            self.latitud = lat
            self.longitud = lng
        super(Sector, self).save(*args, **kwargs)

    def extract_lat_lng_from_link(self, link):
        # Ejemplo: https://www.google.com/maps?q=loc:40.748817,-73.985428&hl=es
        import re
        match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', link)
        if match:
            lat = float(match.group(1))
            lng = float(match.group(2))
            return lat, lng
        match_alt = re.search(r'loc:(-?\d+\.\d+),(-?\d+\.\d+)', link)
        if match_alt:
            lat = float(match_alt.group(1))
            lng = float(match_alt.group(2))
            return lat, lng

        # Enlace en formato https://maps.app.goo.gl/5w8XHiCz9G9peGSSA
        if "maps.app.goo.gl" in link:
            response = requests.get(link)
            url_parts = response.url.split("q=")
            if len(url_parts) > 1:
                location_parts = url_parts[1].split("&")
                if len(location_parts) > 0:
                    location = location_parts[0]
                    lat_lng_parts = location.split(",")
                    if len(lat_lng_parts) == 2:
                        lat = float(lat_lng_parts[0])
                        lng = float(lat_lng_parts[1])
                        return lat, lng
            return None, None

        
    


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