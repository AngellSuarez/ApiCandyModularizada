from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Servicio
from .servicio_serializer import ServicioSerializer


# Create your views here.
class ServicioViewSet(viewsets.ModelViewSet):
    queryset = Servicio.objects.all()
    serializer_class = ServicioSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            servicio = self.get_object()
            if servicio.estado == "Activo":
                servicio.estado = 'Inactivo'
                servicio.save()
                return Response({'message':'Servicio desactivado correctamente'}, status = status.HTTP_200_OK)
            else:
                servicio.delete()
                return Response({'message':'servicio eliminado correctamente'},status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'message':'Servicio eliminado correctamente'}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['patch'])
    def cambiar_estado(self, request, pk=None):
        servicio = self.get_object()
        nuevo_estado = "Activo" if servicio.estado == "Inactivo" else "Inactivo"
        servicio.estado = nuevo_estado
        servicio.save()
        serializer = self.get_serializer(servicio)
        return Response({"message": f"Estado del servicio cambiado a {nuevo_estado}", "data": serializer.data})