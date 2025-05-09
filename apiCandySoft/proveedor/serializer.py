from rest_framework import serializers
from .models import Proveedor

class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = '__all__'

    def validate(self, data):
        tipo_persona = data.get("tipo_persona")
        tipo_documento = data.get("tipo_documento")

        if tipo_documento == "NIT" or tipo_persona == "JURIDICA":
            required_fields = [
                "nombre_empresa", "nombre_representante", "apellido_representante",
                "telefono", "email", "direccion", "ciudad",
                "telefono_representante", "email_representante"
            ]
            for field in required_fields:
                if not data.get(field):
                    raise serializers.ValidationError({
                        field: "Este campo es obligatorio para empresas (persona jurídica o con NIT)."
                    })

        else:
            required_fields = [
                "nombre_representante", "apellido_representante",
                "telefono", "email", "direccion", "ciudad"
            ]
            for field in required_fields:
                if not data.get(field):
                    raise serializers.ValidationError({
                        field: "Este campo es obligatorio para personas naturales."
                    })

            # Campos no permitidos para personas naturales
            if data.get("nombre_empresa"):
                raise serializers.ValidationError({
                    "nombre_empresa": "Este campo no debe ser llenado para personas naturales."
                })
            if data.get("telefono_representante") or data.get("email_representante"):
                raise serializers.ValidationError({
                    "telefono": "No debe llenar estos campos si no es una empresa.",
                    "email_representante": "No debe llenar estos campos si no es una empresa.",
                })

        return data

    def validate_tipo_documento(self, tipo_documento):
        valid_choices = [choice[0] for choice in Proveedor.TIPO_DOCUMENTO_CHOICES]
        if not tipo_documento:
            raise serializers.ValidationError("El tipo de documento es requerido.")
        if tipo_documento not in valid_choices:
            raise serializers.ValidationError("Tipo de documento no válido.")
        return tipo_documento

    def validate_numero_documento(self, numero_documento):
        if not numero_documento:
            raise serializers.ValidationError("El número de documento es requerido.")
        qs = Proveedor.objects.filter(numero_documento=numero_documento)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("El número de documento ya se encuentra registrado.")
        return numero_documento

    def validate_tipo_persona(self, tipo_persona):
        valid_choices = [choice[0] for choice in Proveedor.TIPO_PERSONA_CHOICES]
        if not tipo_persona:
            raise serializers.ValidationError("El tipo de persona es requerido.")
        if tipo_persona not in valid_choices:
            raise serializers.ValidationError(f"Tipo de persona no válido. Opciones válidas: {valid_choices}")
        return tipo_persona

    def validate_telefono(self, telefono):
        if not telefono:
            raise serializers.ValidationError("El teléfono es requerido.")
        qs = Proveedor.objects.filter(telefono=telefono)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("El teléfono ya se encuentra registrado.")
        return telefono

    def validate_email(self, email):
        if not email:
            raise serializers.ValidationError("El email es requerido.")
        qs = Proveedor.objects.filter(email=email)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("El email ya se encuentra registrado.")
        return email
