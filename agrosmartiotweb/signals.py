# signals.py
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Procesos

@receiver(pre_save, sender=Procesos)
def populate_fields(sender, instance, **kwargs):
    if instance.asignado:
        instance.presupuesto = instance.asignado.cobro
        instance.trabajo_realizado = instance.asignado.trabajo_a_realizar

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Jornada, JornadaPorTrato, FinanzasPorTrabajador

@receiver(post_save, sender=Jornada)
@receiver(post_save, sender=JornadaPorTrato)
def actualizar_finanzas_post_save(sender, instance, **kwargs):
    # Pasar el usuario que creó la jornada
    FinanzasPorTrabajador.actualizar_finanzas_trabajador(instance.asignado, instance.created_by)

@receiver(post_delete, sender=Jornada)
@receiver(post_delete, sender=JornadaPorTrato)
def actualizar_finanzas_post_delete(sender, instance, **kwargs):
    # Pasar el usuario que creó la jornada
    FinanzasPorTrabajador.actualizar_finanzas_trabajador(instance.asignado, instance.created_by)
