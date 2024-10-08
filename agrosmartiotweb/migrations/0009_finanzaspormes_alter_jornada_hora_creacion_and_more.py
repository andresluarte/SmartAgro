# Generated by Django 4.2.3 on 2024-10-07 21:17

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('agrosmartiotweb', '0008_alter_jornada_hora_creacion_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='FinanzasPorMes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mes', models.DateField()),
                ('total_gasto_jornada_horas', models.IntegerField(blank=True, default=0, editable=False, null=True)),
                ('total_gasto_jornada_trato', models.IntegerField(blank=True, default=0, editable=False, null=True)),
                ('total_gasto_mensual', models.IntegerField(blank=True, default=0, editable=False, null=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='finanzas_por_mes_creadas', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-mes'],
                'unique_together': {('user', 'mes')},
            },
        ),
        migrations.AlterField(
            model_name='jornada',
            name='hora_creacion',
            field=models.TimeField(default=datetime.time(18, 17, 47, 419273), editable=False),
        ),
        migrations.AlterField(
            model_name='jornadaportrato',
            name='hora_creacion',
            field=models.TimeField(default=datetime.time(18, 17, 47, 420274), editable=False),
        ),
        migrations.AlterField(
            model_name='procesos',
            name='hora_creacion',
            field=models.TimeField(default=datetime.time(18, 17, 47, 418274), editable=False),
        ),
        migrations.DeleteModel(
            name='FinanzasPorTrabajadorPorMes',
        ),
    ]
