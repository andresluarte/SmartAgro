# Generated by Django 4.2.3 on 2024-09-24 20:22

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('agrosmartiotweb', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='empresa',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='empresas', to='agrosmartiotweb.empresaofundo'),
        ),
        migrations.AlterField(
            model_name='jornada',
            name='hora_creacion',
            field=models.TimeField(default=datetime.time(17, 22, 47, 187087), editable=False),
        ),
        migrations.AlterField(
            model_name='procesos',
            name='hora_creacion',
            field=models.TimeField(default=datetime.time(17, 22, 47, 186090), editable=False),
        ),
        migrations.CreateModel(
            name='JornadaPorTrato',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateField(default=datetime.date.today, editable=False)),
                ('hora_creacion', models.TimeField(default=datetime.time(17, 22, 47, 188045), editable=False)),
                ('fecha', models.DateField()),
                ('estado', models.CharField(choices=[('Por Realizar', 'Por Realizar'), ('En Proceso', 'En Proceso'), ('Terminado', 'Terminado')], default='Por Realizar', max_length=15)),
                ('nombre_tarea_1', models.CharField(max_length=100)),
                ('cobro_tarea_1', models.IntegerField(blank=True, null=True)),
                ('nombre_tarea_2', models.CharField(blank=True, max_length=100, null=True)),
                ('cobro_tarea_2', models.IntegerField(blank=True, null=True)),
                ('nombre_tarea_3', models.CharField(blank=True, max_length=100, null=True)),
                ('cobro_tarea_3', models.IntegerField(blank=True, null=True)),
                ('nombre_extra_1', models.CharField(blank=True, max_length=100, null=True)),
                ('gasto_extra_1', models.IntegerField(blank=True, null=True)),
                ('nombre_extra_2', models.CharField(blank=True, max_length=100, null=True)),
                ('gasto_extra_2', models.IntegerField(blank=True, null=True)),
                ('nombre_extra_3', models.CharField(blank=True, max_length=100, null=True)),
                ('gasto_extra_3', models.IntegerField(blank=True, null=True)),
                ('detalle_gasto_total_tareas', models.IntegerField(blank=True, editable=False, null=True)),
                ('detalle_gastos_total_extras', models.IntegerField(blank=True, editable=False, null=True)),
                ('total_gasto_jornada', models.IntegerField(blank=True, editable=False, null=True)),
                ('asignado', models.ForeignKey(max_length=50, null=True, on_delete=django.db.models.deletion.CASCADE, to='agrosmartiotweb.trabajador')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jornadas_por_trato_creadas', to=settings.AUTH_USER_MODEL)),
                ('huerto', models.ForeignKey(blank=True, max_length=50, null=True, on_delete=django.db.models.deletion.CASCADE, to='agrosmartiotweb.huerto')),
                ('lote', models.ForeignKey(blank=True, max_length=50, null=True, on_delete=django.db.models.deletion.CASCADE, to='agrosmartiotweb.lote')),
                ('sector', models.ForeignKey(blank=True, max_length=50, null=True, on_delete=django.db.models.deletion.CASCADE, to='agrosmartiotweb.sector')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-fecha_creacion', '-hora_creacion'],
            },
        ),
    ]
