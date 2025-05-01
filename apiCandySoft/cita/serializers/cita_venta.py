from rest_framework import serializers
from django.db import models
from datetime import date, time
import requests;

from usuario.models.manicurista import Manicurista
from usuario.models.cliente import Cliente
from ..models.cita_venta import CitaVenta
from ..models.estado_cita import EstadoCita

class CitaVentaSerializer(serializers.ModelSerializer):
    cliente_id = serializers.PrimaryKeyRelatedField(queryset=Cliente.objects.all())
    manicurista_id = serializers.PrimaryKeyRelatedField(queryset=Manicurista.objects.all())
    estado_id = serializers.PrimaryKeyRelatedField(queryset=EstadoCita.objects.all())

    cliente_nombre = serializers.SerializerMethodField()
    manicurista_nombre = serializers.SerializerMethodField()
    estado_nombre = serializers.SerializerMethodField()

    class Meta:
        model = CitaVenta
        fields = [
            'id',
            'cliente_id',
            'cliente_nombre',
            'manicurista_id',
            'manicurista_nombre',
            'estado_id',
            'estado_nombre',
            'Fecha',
            'Hora',
            'Descripcion',
            'Total',
        ]

    def get_cliente_nombre(self, obj):
        return f"{obj.cliente_id.nombre} {obj.cliente_id.apellido}"

    def get_manicurista_nombre(self, obj):
        return f"{obj.manicurista_id.nombre} {obj.manicurista_id.apellido}"

    def get_estado_nombre(self, obj):
        return obj.estado_id.Estado