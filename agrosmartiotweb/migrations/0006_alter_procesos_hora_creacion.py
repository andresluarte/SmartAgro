# Generated by Django 4.2.3 on 2023-08-27 21:08

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agrosmartiotweb', '0005_alter_jornada_huerto_alter_jornada_lote_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='procesos',
            name='hora_creacion',
            field=models.TimeField(default=datetime.time(17, 8, 46, 79138), editable=False),
        ),
    ]
