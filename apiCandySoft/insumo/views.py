from django.shortcuts import render
from rest_framework import  viewsets, status, permissions;
from rest_framework.response import Response;
from rest_framework.decorators import action;
from rest_framework.permissions import AllowAny;
from compra.models import CompraInsumo
from .models import Marca, Insumo
from .serializer import MarcaSerializer, InsumoSerializer
# Create your views here.

from permisos.custom_permissions import TienePermisoModulo

class MarcaViewSet(viewsets.ModelViewSet):
    queryset = Marca.objects.all()
    serializer_class = MarcaSerializer;
    permission_classes = [TienePermisoModulo("Insumo")];

    
    
    def destroy(self, request, *args, **kwargs):
        marca = self.get_object()
        if Insumo.objects.filter(marca_id=marca).exists():
            return Response(
                {"eliminado": False, "message": "No se puede eliminar la marca porque está asociada a uno o más insumos."},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_destroy(marca)
        return Response({"eliminado": True}, status=status.HTTP_200_OK)

class InsumoViewSet(viewsets.ModelViewSet):
    queryset = Insumo.objects.all()
    serializer_class = InsumoSerializer
    permission_classes = [TienePermisoModulo("Insumo")];

    def destroy(self, request, *args, **kwargs):
        insumo = self.get_object()

        # Obtener solo CompraInsumo donde el insumo esté relacionado
        compras_relacionadas = CompraInsumo.objects.filter(insumo_id=insumo)

        # Verificar si alguna de esas compras tiene estado distinto de "Completada" (id ≠ 3) cancelada 4
        hay_compra_no_completada = compras_relacionadas.filter(
            compra_id__estadoCompra_id__id__in=[1, 2]  # estados distintos a 3 o 4
        ).exists()

        if hay_compra_no_completada:
            return Response(
                {"eliminado": False, "message": "No se puede eliminar el insumo porque está en una compra no completada o cancelada."},
                status=status.HTTP_400_BAD_REQUEST
            )

        self.perform_destroy(insumo)
        return Response({"eliminado": True}, status=status.HTTP_200_OK)
    @action(detail=False, methods=['get'])
    def disponibles(self, request):
        """
        Retorna todos los insumos que NO están inactivos ni agotados.
        Es decir: solo los que están en estado 'Activo' o 'Bajo'
        """
        insumos_disponibles = self.queryset.filter(estado__in=['Activo', 'Bajo'])
        serializer = self.get_serializer(insumos_disponibles, many=True)
        return Response(serializer.data)