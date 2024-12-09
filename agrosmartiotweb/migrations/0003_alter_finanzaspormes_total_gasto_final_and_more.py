# Generated by Django 4.2.3 on 2024-10-28 03:23

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agrosmartiotweb', '0002_alter_jornada_hora_creacion_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='finanzaspormes',
            name='total_gasto_final',
            field=models.IntegerField(blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='finanzaspormes',
            name='total_gasto_jornadas',
            field=models.IntegerField(blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='finanzaspormes',
            name='total_gasto_jornadas_por_trato',
            field=models.IntegerField(blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='jornada',
            name='hora_creacion',
            field=models.TimeField(default=datetime.time(0, 23, 16, 833498), editable=False),
        ),
        migrations.AlterField(
            model_name='jornadaportrato',
            name='hora_creacion',
            field=models.TimeField(default=datetime.time(0, 23, 16, 834498), editable=False),
        ),
        migrations.AlterField(
            model_name='procesos',
            name='hora_creacion',
            field=models.TimeField(default=datetime.time(0, 23, 16, 832498), editable=False),
        ),
    ]
