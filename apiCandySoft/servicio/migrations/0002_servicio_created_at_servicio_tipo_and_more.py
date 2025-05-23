# Generated by Django 5.2 on 2025-05-13 21:12

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servicio', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicio',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='servicio',
            name='tipo',
            field=models.CharField(choices=[('Manicure', 'Manicure'), ('Pedicure', 'Pedicure'), ('Uñas acrílicas', 'Uñas Acrílicas')], default='Manicure', max_length=40),
        ),
        migrations.AlterField(
            model_name='servicio',
            name='estado',
            field=models.CharField(choices=[('Activo', 'Activo'), ('Inactivo', 'Inactivo')], default='Activo', max_length=40),
        ),
    ]
