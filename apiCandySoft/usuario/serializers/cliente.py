from rest_framework import serializers
from ..models.usuario import Usuario
from ..models.cliente import Cliente
from rol.models import Rol
from django.contrib.auth.password_validation import validate_password

class ClienteSerializer(serializers.ModelSerializer):
    # Entrada en POST/PUT/PATCH
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    rol_id = serializers.PrimaryKeyRelatedField(queryset=Rol.objects.all(), write_only=True)

    # Salida en GET
    username_out = serializers.SerializerMethodField(read_only=True)
    rol_id_out = serializers.SerializerMethodField(read_only=True)
    usuario_id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Cliente
        fields = [
            'username', 'password', 'rol_id',
            'nombre', 'apellido', 'tipo_documento', 'numero_documento',
            'correo', 'celular', 'estado',
            'username_out', 'rol_id_out','usuario_id'
        ]

    def get_username_out(self, obj):
        return obj.usuario.username if obj.usuario else None

    def get_rol_id_out(self, obj):
        return obj.usuario.rol_id.id if obj.usuario and obj.usuario.rol_id else None
    
    def get_usuario_id(self, obj):
        return obj.usuario.id if obj.usuario else None

    def validate_estado(self, estado):
        estados_validos = [choice[0] for choice in Cliente.ESTADOS_CHOICES]
        if estado not in estados_validos:
            raise serializers.ValidationError(f"Estado no valido, las opciones son: {estados_validos}")
        return estado

    def validate_tipo_documento(self, tipo_documento):
        tipos_validos = [choice[0] for choice in Cliente.TIPO_DOCUMENTO_CHOICES]
        if tipo_documento not in tipos_validos:
            raise serializers.ValidationError(f"Tipo de documento no valido, las opciones son: {tipos_validos}")
        return tipo_documento

    def validate_numero_documento(self, numero_documento):
        instance = getattr(self, 'instance', None)
        if Cliente.objects.exclude(pk=instance.pk if instance else None).filter(numero_documento=numero_documento).exists():
            raise serializers.ValidationError("El numero de documento ya esta registrado")
        return numero_documento

    def validate_correo(self, correo):
        instance = getattr(self, 'instance', None)
        usuario_id = None
        if instance and hasattr(instance, 'usuario'):
            usuario_id = instance.usuario.pk
        if Cliente.objects.exclude(pk=instance.pk if instance else None).filter(correo=correo).exists():
            raise serializers.ValidationError("El correo inscrito ya existe")
        if Usuario.objects.exclude(pk=usuario_id).filter(correo=correo).exists():
            raise serializers.ValidationError("El correo inscrito ya existe")
        return correo

    """ def validate_celular(self, celular):
        instance = getattr(self, 'instance', None)
        if Cliente.objects.exclude(pk=instance.pk if instance else None).filter(celular=celular).exists():
            raise serializers.ValidationError("El celular inscrito ya existe")
        return celular """

    def validate_nombre(self, nombre):
        if not nombre:
            raise serializers.ValidationError("El nombre no puede estar en blanco")
        if len(nombre) < 3:
            raise serializers.ValidationError("El nombre debe tener al menos 3 caracteres")
        if nombre.isdigit():
            raise serializers.ValidationError("El nombre no puede ser solo numeros")
        return nombre

    def validate_apellido(self, apellido):
        if not apellido:
            raise serializers.ValidationError("El apellido no puede estar en blanco")
        if len(apellido) < 3:
            raise serializers.ValidationError("El apellido debe tener al menos 3 caracteres")
        if apellido.isdigit():
            raise serializers.ValidationError("El apellido no puede ser solo numeros")
        return apellido

    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        rol_id = validated_data.pop('rol_id')

        correo = validated_data.get('correo')
        nombre = validated_data.get('nombre', '')
        apellido = validated_data.get('apellido', '')

        usuario = Usuario.objects.create_user(
            username=username,
            password=password,
            rol_id=rol_id,
            correo=correo,
            nombre=nombre,
            apellido=apellido
        )

        cliente = Cliente.objects.create(usuario=usuario, **validated_data)
        return cliente

    def update(self, instance, validated_data):
        usuario = instance.usuario

        usuario_fields = ['nombre', 'apellido', 'correo', 'username', 'password']
        for field in usuario_fields:
            if field in validated_data:
                value = validated_data.pop(field)
                if field == 'password':
                    usuario.set_password(value)
                else:
                    setattr(usuario, field, value)

        usuario.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
