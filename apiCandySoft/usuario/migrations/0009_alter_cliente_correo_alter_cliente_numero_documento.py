# Generated by Django 5.2 on 2025-06-11 01:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuario', '0008_alter_usuario_numero_documento'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cliente',
            name='correo',
            field=models.EmailField(max_length=40, unique=True),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='numero_documento',
            field=models.CharField(max_length=15, unique=True),
        ),
    ]
