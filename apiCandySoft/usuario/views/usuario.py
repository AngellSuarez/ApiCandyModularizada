from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from ..serializers.usuario import UsuarioSerializer
from ..models.usuario import Usuario

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    
    # Sobreescribimos el método destroy para cambiar el estado en lugar de eliminar
    def destroy(self, request, *args, **kwargs):
        usuario = self.get_object()
        usuario.estado = "inactivo"
        usuario.save()
        return Response({"message": "Usuario desactivado correctamente"}, status=status.HTTP_200_OK)
    
    # Acción personalizada para cambiar el estado
    @action(detail=True, methods=['patch'])
    def cambiar_estado(self, request, pk=None):
        usuario = self.get_object()
        nuevo_estado = "activo" if usuario.estado == "inactivo" else "inactivo"
        usuario.estado = nuevo_estado
        usuario.save()
        serializer = self.get_serializer(usuario)
        return Response({"message": f"Estado del usuario cambiado a {nuevo_estado}", "data": serializer.data})
    
    # Filtrar usuarios por estado
    @action(detail=False, methods=['get'])
    def activos(self, request):
        usuarios_activos = Usuario.objects.filter(estado="activo")
        serializer = self.get_serializer(usuarios_activos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def inactivos(self, request):
        usuarios_inactivos = Usuario.objects.filter(estado="inactivo")
        serializer = self.get_serializer(usuarios_inactivos, many=True)
        return Response(serializer.data)
    
    # Filtrar usuarios por rol
    @action(detail=False, methods=['get'])
    def por_rol(self, request):
        rol_id = request.query_params.get('rol_id', None)
        if rol_id:
            usuarios = Usuario.objects.filter(rol_id=rol_id)
            serializer = self.get_serializer(usuarios, many=True)
            return Response(serializer.data)
        return Response({"error": "Debe especificar un rol_id"}, status=status.HTTP_400_BAD_REQUEST)
