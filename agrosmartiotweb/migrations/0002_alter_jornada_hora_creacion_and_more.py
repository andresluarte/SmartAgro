# Generated by Django 4.2.3 on 2025-02-04 01:41

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agrosmartiotweb', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jornada',
            name='hora_creacion',
            field=models.TimeField(default=datetime.time(22, 41, 37, 107070), editable=False),
        ),
        migrations.AlterField(
            model_name='jornadaportrato',
            name='hora_creacion',
            field=models.TimeField(default=datetime.time(22, 41, 37, 108069), editable=False),
        ),
        migrations.AlterField(
            model_name='procesos',
            name='hora_creacion',
            field=models.TimeField(default=datetime.time(22, 41, 37, 106069), editable=False),
        ),
    ]
