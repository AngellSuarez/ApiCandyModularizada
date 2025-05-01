from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from ..serializers.manicurista import ManicuristaSerializer
from ..serializers.usuario import UsuarioSerializer

from ..models.usuario import Usuario
from ..models.manicurista import Manicurista

class ManicuristaViewSet(viewsets.ModelViewSet):
    queryset = Manicurista.objects.all()
    serializer_class = ManicuristaSerializer
    
    # Sobreescribimos el método destroy para cambiar el estado en lugar de eliminar
    def destroy(self, request, *args, **kwargs):
        manicurista = self.get_object()
        manicurista.estado = "inactivo"
        manicurista.save()
        return Response({"message": "Manicurista desactivado correctamente"}, status=status.HTTP_200_OK)
    
    # Acción personalizada para cambiar el estado
    @action(detail=True, methods=['patch'])
    def cambiar_estado(self, request, pk=None):
        manicurista = self.get_object()
        nuevo_estado = "activo" if manicurista.estado == "inactivo" else "inactivo"
        manicurista.estado = nuevo_estado
        manicurista.save()
        serializer = self.get_serializer(manicurista)
        return Response({"message": f"Estado del manicurista cambiado a {nuevo_estado}", "data": serializer.data})
    
    # Filtrar manicuristas por estado
    @action(detail=False, methods=['get'])
    def activos(self, request):
        manicuristas_activos = Manicurista.objects.filter(estado="activo")
        serializer = self.get_serializer(manicuristas_activos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def inactivos(self, request):
        manicuristas_inactivos = Manicurista.objects.filter(estado="inactivo")
        serializer = self.get_serializer(manicuristas_inactivos, many=True)
        return Response(serializer.data)
    
    # Buscar manicurista por número de documento
    @action(detail=False, methods=['get'])
    def por_documento(self, request):
        numero = request.query_params.get('numero', None)
        tipo = request.query_params.get('tipo', None)
        
        if numero:
            query = {'numero_documento': numero}
            if tipo:
                query['tipo_documento'] = tipo
                
            manicuristas = Manicurista.objects.filter(**query)
            serializer = self.get_serializer(manicuristas, many=True)
            return Response(serializer.data)
        return Response({"error": "Debe especificar un número de documento"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Filtrar manicuristas por fecha de contratación
    @action(detail=False, methods=['get'])
    def por_fecha_contratacion(self, request):
        desde = request.query_params.get('desde', None)
        hasta = request.query_params.get('hasta', None)
        
        query = {}
        if desde:
            query['fecha_contratacion__gte'] = desde
        if hasta:
            query['fecha_contratacion__lte'] = hasta
            
        if query:
            manicuristas = Manicurista.objects.filter(**query)
            serializer = self.get_serializer(manicuristas, many=True)
            return Response(serializer.data)
        return Response({"error": "Debe especificar al menos una fecha (desde o hasta)"}, status=status.HTTP_400_BAD_REQUEST)