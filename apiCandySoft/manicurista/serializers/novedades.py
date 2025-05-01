from rest_framework import serializers;
from datetime import date,time, timedelta;
from django.db import models;
from ..models.novedades import Novedades
from usuario.models.manicurista import Manicurista

class NovedadesSerializer(serializers.ModelSerializer):
    manicurista_id = serializers.PrimaryKeyRelatedField(queryset=Manicurista.objects.all())
    manicurista_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Novedades
        fields = [
            'id',
            'manicurista_id',
            'Fecha',
            'HoraEntrada',
            'HoraSalida',
            'Motivo',
            'manicurista_nombre',
        ]

    def get_manicurista_nombre(self, obj):
        return f"{obj.manicurista_id.nombre} {obj.manicurista_id.apellido}"

    def validate_Fecha(self, value):
        max_fecha = date.today() + timedelta(days=7)
        if value > max_fecha:
            raise serializers.ValidationError("La fecha no puede superar 7 días desde hoy.")
        return value

    def validate_HoraEntrada(self, value):
        if value < time(8, 0) or value > time(18, 0):
            raise serializers.ValidationError("La hora de entrada debe estar entre las 8:00 AM y las 6:00 PM.")
        return value

    def validate_HoraSalida(self, value):
        if value < time(8, 0) or value > time(18, 0):
            raise serializers.ValidationError("La hora de salida debe estar entre las 8:00 AM y las 6:00 PM.")
        return value

    def validate(self, data):
        hora_entrada = data.get("HoraEntrada")
        hora_salida = data.get("HoraSalida")
        if hora_entrada and hora_salida and hora_salida <= hora_entrada:
            raise serializers.ValidationError("La hora de salida debe ser posterior a la hora de entrada.")
        return data