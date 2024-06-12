# Generated by Django 4.2.3 on 2023-08-27 21:05

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('agrosmartiotweb', '0004_procesos_huerto_procesos_lote_procesos_sector_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jornada',
            name='huerto',
            field=models.ForeignKey(blank=True, max_length=50, null=True, on_delete=django.db.models.deletion.CASCADE, to='agrosmartiotweb.huerto'),
        ),
        migrations.AlterField(
            model_name='jornada',
            name='lote',
            field=models.ForeignKey(blank=True, max_length=50, null=True, on_delete=django.db.models.deletion.CASCADE, to='agrosmartiotweb.lote'),
        ),
        migrations.AlterField(
            model_name='jornada',
            name='sector',
            field=models.ForeignKey(blank=True, max_length=50, null=True, on_delete=django.db.models.deletion.CASCADE, to='agrosmartiotweb.sector'),
        ),
        migrations.AlterField(
            model_name='procesos',
            name='hora_creacion',
            field=models.TimeField(default=datetime.time(17, 5, 51, 144713), editable=False),
        ),
    ]
