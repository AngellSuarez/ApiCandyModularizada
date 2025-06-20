# Generated by Django 5.2 on 2025-06-09 05:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuario', '0004_alter_cliente_estado_alter_manicurista_estado'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='numero_documento',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='usuario',
            name='tipo_documento',
            field=models.CharField(blank=True, choices=[('CC', 'cedula de ciudadania'), ('CE', 'cedula de extranjeria'), ('PA', 'pasaporte')], default='CC', max_length=2, null=True),
        ),
    ]
