# Generated by Django 4.2.3 on 2024-09-27 22:07

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agrosmartiotweb', '0009_sector_google_maps_link_sector_latitud_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jornada',
            name='hora_creacion',
            field=models.TimeField(default=datetime.time(19, 7, 42, 994294), editable=False),
        ),
        migrations.AlterField(
            model_name='jornadaportrato',
            name='hora_creacion',
            field=models.TimeField(default=datetime.time(19, 7, 42, 995291), editable=False),
        ),
        migrations.AlterField(
            model_name='procesos',
            name='hora_creacion',
            field=models.TimeField(default=datetime.time(19, 7, 42, 992300), editable=False),
        ),
    ]
