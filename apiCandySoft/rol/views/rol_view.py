from rest_framework import viewsets, status, permissions;
from rest_framework.response import Response;
from rest_framework.decorators import action;
from rest_framework.permissions import AllowAny;

from ..models import Rol
from ..serializers import RolSerializer

class RolViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all();
    serializer_class = RolSerializer;
    permission_classes = [AllowAny];
    
    #cambiar estado
    @action(detail=True, methods=['patch'])
    def cambiar_estado(self,request,pk=None):
        rol = self.get_object();
        nuevo_estado = "activo" if rol.estado == "inactivo" else "inactivo";
        rol.estado = nuevo_estado;
        rol.save();
        serializer = self.get_serializer(rol)
        return Response({"message":f"El estado del rol cambio a {nuevo_estado} correctamente","data":serializer.data});
    
    #cambiar el eliminar (destroy en django para inactivo)
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object();
        instance.estado = "inactivo";
        instance.save()
        return Response({"message":"Rol desactivado correctamente"}, status=status.HTTP_200_OK);
    
    #filtrar roles por estado
    @action(detail=False,methods=['get'])
    def activos(self,request):
        roles_activos = Rol.objects.filter(estado="activo");
        serializer = self.get_serializer(roles_activos, many=True);
        return Response(serializer.data);
    
    @action(detail=False,methods=["get"])
    def inactivos(self,request):
        roles_inactivos = Rol.objects.filter(estado="inactivo");
        serializer = self.get_serializer(roles_inactivos, many=True);
        return Response(serializer.data);
    