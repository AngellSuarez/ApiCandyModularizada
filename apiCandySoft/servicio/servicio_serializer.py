from rest_framework import serializers
from .models import Servicio
import requests
import os
from django.db import models

class ServicioSerializer(serializers.ModelSerializer):
    imagen = serializers.ImageField(write_only=True, required=False)  # Campo para recibir la imagen como archivo

    class Meta:
        model = Servicio
        fields = '__all__'

    def validate_nombre(self, nombre):
        if not nombre:
            raise serializers.ValidationError("El nombre es requerido")
        if len(nombre) < 3:
            raise serializers.ValidationError("El nombre debe tener al menos 3 caracteres")
        if nombre.isdigit():
            raise serializers.ValidationError("El nombre no puede contener solo numeros")
        return nombre

    def validate_precio(self, precio):
        if precio < 0:
            raise serializers.ValidationError("El precio no puede ser negativo")
        if not precio:
            raise serializers.ValidationError("El precio es requerido")
        return precio

    def validate_estado(self, estado):
        estado_choices = [choice[0] for choice in Servicio.ESTADOS_CHOICES]
        if estado not in estado_choices:
            raise serializers.ValidationError(f"Estado no valido, las opciones validas son: {estado_choices}")
        if not estado:
            raise serializers.ValidationError("El estado es requerido")
        return estado

    def create(self, validated_data):
        imagen = validated_data.pop('imagen', None)
        if imagen:
            url_imagen = self._subir_imagen_imgbb(imagen)
            validated_data['url_imagen'] = url_imagen
        else:
            validated_data['url_imagen'] = "https://ibb.co/zWhfbh8D"  # URL por defecto

        return super().create(validated_data)

    def update(self, instance, validated_data):
        imagen = validated_data.pop('imagen', None)
        if imagen:
            url_imagen = self._subir_imagen_imgbb(imagen)
            validated_data['url_imagen'] = url_imagen
        return super().update(instance, validated_data)

    def _subir_imagen_imgbb(self, imagen):
        """Sube la imagen a ImgBB y devuelve la URL de la imagen."""
        IMGBB_API_KEY = os.getenv('IMGBB_API_KEY')
        if not IMGBB_API_KEY:
            return "https://ibb.co/zWhfbh8D"  # Retorna imagen por defecto si no hay API Key

        url = "https://api.imgbb.com/1/upload"
        files = {"image": imagen}  # Subir archivo directamente
        payload = {"key": IMGBB_API_KEY}

        try:
            res = requests.post(url, files=files, data=payload)
            res.raise_for_status()
            response_json = res.json()
            return response_json.get('data', {}).get('url', "https://ibb.co/zWhfbh8D")
        except requests.exceptions.RequestException:
            return "https://ibb.co/zWhfbh8D"  # En caso de error, usar imagen por defecto
