# Generated by Django 4.2.3 on 2024-10-07 04:24

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
            field=models.TimeField(default=datetime.time(1, 24, 2, 364039), editable=False),
        ),
        migrations.AlterField(
            model_name='jornadaportrato',
            name='hora_creacion',
            field=models.TimeField(default=datetime.time(1, 24, 2, 367038), editable=False),
        ),
        migrations.AlterField(
            model_name='procesos',
            name='hora_creacion',
            field=models.TimeField(default=datetime.time(1, 24, 2, 362039), editable=False),
        ),
    ]
