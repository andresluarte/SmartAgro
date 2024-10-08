# Generated by Django 4.2.3 on 2024-10-07 04:25

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agrosmartiotweb', '0002_alter_jornada_hora_creacion_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='trabajador',
            name='foto',
            field=models.ImageField(blank=True, null=True, upload_to='fundos/fotos/'),
        ),
        migrations.AlterField(
            model_name='jornada',
            name='hora_creacion',
            field=models.TimeField(default=datetime.time(1, 25, 17, 64873), editable=False),
        ),
        migrations.AlterField(
            model_name='jornadaportrato',
            name='hora_creacion',
            field=models.TimeField(default=datetime.time(1, 25, 17, 65872), editable=False),
        ),
        migrations.AlterField(
            model_name='procesos',
            name='hora_creacion',
            field=models.TimeField(default=datetime.time(1, 25, 17, 63872), editable=False),
        ),
    ]
