from rest_framework import serializers
from django.db import models
from datetime import date, time
import requests;

from servicio.models import Servicio 
from ..models.cita_venta import CitaVenta
from ..models.servicio_cita import ServicioCita

class ServicioCitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicioCita
        fields = '__all__'
        
    def validate_cita_id(self, cita_id):
        try:
            CitaVenta.objects.get(id=cita_id.id)
        except CitaVenta.DoesNotExist:
            raise serializers.ValidationError("La cita no existe")
        if not cita_id:
            raise serializers.ValidationError("La cita es requerida")
        return cita_id
        
    def validate_servicio_id(self, servicio_id):
        try:
            Servicio.objects.get(id=servicio_id.id)
        except Servicio.DoesNotExist:
            raise serializers.ValidationError("El servicio no existe")
        if not servicio_id:
            raise serializers.ValidationError("El servicio es requerido")
        return servicio_id
        
    def validate_subtotal(self, subtotal):
        if subtotal < 0:
            raise serializers.ValidationError("El subtotal no puede ser negativo")
        return subtotal
        
    def validate(self, data):   
        # Validar que el servicio no este ya en la cita
        if 'cita_id' in data and 'servicio_id' in data:
            # Eliminar la instancia actual de la consulta al momento de actualizar
            query_existente = ServicioCita.objects.filter(
                cita_id=data['cita_id'],
                servicio_id=data['servicio_id'],
            )
            if self.instance:
                query_existente = query_existente.exclude(id=self.instance.id)
            if query_existente.exists():
                raise serializers.ValidationError({
                    "non_field_errors": "El servicio ya se encuentra registrado en la cita"
                })
                
        # Si es una creación y no se proporcionó subtotal, usar el precio del servicio
        if not self.instance and 'servicio_id' in data and 'subtotal' not in data:
            servicio = data['servicio_id']
            data['subtotal'] = servicio.precio  # Asumiendo que el servicio tiene un campo 'precio'
            
        return data
        
    def create(self, validated_data):
        servicioCita = super().create(validated_data)
        self._actualizar_total_cita(servicioCita.cita_id)
        return servicioCita
        
    def update(self, instance, validated_data):
        servicioCita = super().update(instance, validated_data)
        self._actualizar_total_cita(servicioCita.cita_id)
        return servicioCita
        
    def _actualizar_total_cita(self, cita):
        nuevo_total = ServicioCita.objects.filter(cita_id=cita).aggregate(
            total=models.Sum('subtotal')
        )['total'] or 0
        cita.Total = nuevo_total
        cita.save()