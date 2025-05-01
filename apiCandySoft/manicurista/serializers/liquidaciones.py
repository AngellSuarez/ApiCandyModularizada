from rest_framework import serializers;
from datetime import date,time, timedelta;
from django.db import models;
from ..models.novedades import Novedades
from usuario.models.manicurista import Manicurista

from rest_framework import serializers;
from datetime import date,time, timedelta;
from django.db import models;

from ..models.liquidaciones import Liquidacion
from usuario.models.manicurista import Manicurista
from cita.models.cita_venta import CitaVenta

class LiquidacionSerializer(serializers.ModelSerializer):
    manicurista_id = serializers.PrimaryKeyRelatedField(queryset=Manicurista.objects.all())
    manicurista_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Liquidacion
        fields = [
            'id',
            'manicurista_id',
            'FechaInicial',
            'FechaFinal',
            'TotalGenerado',
            'Comision',
            'Local',
            'manicurista_nombre',
        ]

    def get_manicurista_nombre(self, obj):
        return f"{obj.manicurista_id.nombre} {obj.manicurista_id.apellido}"

    def validate_manicurista_id(self, manicurista_id):
        if not manicurista_id:
            raise serializers.ValidationError("El manicurista es requerido")
        return manicurista_id

    def validate(self, data):
        manicurista = data.get('manicurista_id')
        fecha_inicial = data.get('FechaInicial')
        fecha_final = data.get('FechaFinal')

        if not (manicurista and fecha_inicial and fecha_final):
            raise serializers.ValidationError("Debe proporcionar manicurista, fecha inicial y fecha final")

        if fecha_final != date.today():
            raise serializers.ValidationError({
                "FechaFinal": "La fecha final debe ser la fecha actual"
            })

        if fecha_inicial != fecha_final - timedelta(days=5):
            raise serializers.ValidationError({
                "FechaInicial": f"La fecha inicial debe ser exactamente 5 días antes de la fecha final ({fecha_final - timedelta(days=5)})"
            })

        liquidaciones_existentes = Liquidacion.objects.filter(
            manicurista_id=manicurista,
            FechaInicial=fecha_inicial,
            FechaFinal=fecha_final
        )
        if liquidaciones_existentes.exists():
            raise serializers.ValidationError("Ya existe una liquidación para este rango de fechas")

        citas_venta = CitaVenta.objects.filter(
            manicurista_id=manicurista,
            Fecha__gte=fecha_inicial,
            Fecha__lte=fecha_final
        )

        total_generado = sum(cita.Total for cita in citas_venta)
        data['TotalGenerado'] = total_generado
        data['Comision'] = total_generado * 0.5
        data['Local'] = total_generado * 0.5

        return data

