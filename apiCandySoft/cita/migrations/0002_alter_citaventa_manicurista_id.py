# Generated by Django 5.2 on 2025-06-11 04:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cita', '0001_initial'),
        ('usuario', '0010_alter_manicurista_celular_alter_manicurista_correo_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='citaventa',
            name='manicurista_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='usuario.manicurista'),
        ),
    ]
