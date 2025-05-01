from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from ..serializers.cliente import ClienteSerializer
from ..serializers.usuario import UsuarioSerializer

from ..models.usuario import Usuario
from ..models.cliente import Cliente

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    
    # Sobreescribimos el método destroy para cambiar el estado en lugar de eliminar
    def destroy(self, request, *args, **kwargs):
        cliente = self.get_object()
        cliente.estado = "inactivo"
        cliente.save()
        return Response({"message": "Cliente desactivado correctamente"}, status=status.HTTP_200_OK)
    
    # Acción personalizada para cambiar el estado
    @action(detail=True, methods=['patch'])
    def cambiar_estado(self, request, pk=None):
        cliente = self.get_object()
        nuevo_estado = "activo" if cliente.estado == "inactivo" else "inactivo"
        cliente.estado = nuevo_estado
        cliente.save()
        serializer = self.get_serializer(cliente)
        return Response({"message": f"Estado del cliente cambiado a {nuevo_estado}", "data": serializer.data})
    
    # Filtrar clientes por estado
    @action(detail=False, methods=['get'])
    def activos(self, request):
        clientes_activos = Cliente.objects.filter(estado="activo")
        serializer = self.get_serializer(clientes_activos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def inactivos(self, request):
        clientes_inactivos = Cliente.objects.filter(estado="inactivo")
        serializer = self.get_serializer(clientes_inactivos, many=True)
        return Response(serializer.data)
    
    # Buscar cliente por número de documento
    @action(detail=False, methods=['get'])
    def por_documento(self, request):
        numero = request.query_params.get('numero', None)
        tipo = request.query_params.get('tipo', None)
        
        if numero:
            query = {'numero_documento': numero}
            if tipo:
                query['tipo_documento'] = tipo
                
            clientes = Cliente.objects.filter(**query)
            serializer = self.get_serializer(clientes, many=True)
            return Response(serializer.data)
        return Response({"error": "Debe especificar un número de documento"}, status=status.HTTP_400_BAD_REQUEST)
