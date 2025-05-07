from rest_framework import viewsets, status, permissions;
from rest_framework.response import Response;
from rest_framework.decorators import action;
from rest_framework.permissions import AllowAny;

from ..models import Rol
from ..models import Permiso_Rol
from ..serializers import RolSerializer
from ..serializers import PermisoRolSerializer
from usuario.models.usuario import Usuario

""" from ...utils.decorador_permisos import verificar_permiso """

#@verificar_permiso('rol')
class RolViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all();
    serializer_class = RolSerializer;
    permission_classes = [AllowAny];
    
    #detalles con servicios
    @action(detail=True, methods=['get'])
    def detalle_con_permiso(self,request,pk=None):
        rol = self.get_object()
        
        #obtener los permisos
        permiso_rol = Permiso_Rol.objects.filter(rol_id = rol.id).select_related("permiso_id")
        
        permiso_serializado = [
            {
                "id":pr.permiso_id.id,
                "modulo":pr.permiso_id.modulo,
            }
            for pr in permiso_rol
        ]
        
        data = {
            "rol": {
                "id": rol.id,
                "nombre": rol.nombre,
                "descripcion": rol.descripcion,
                "estado": rol.estado
            },
            "modulos":permiso_serializado
        }
        
        return Response(data)
    
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

        usuarios_activos = Usuario.objects.filter(rol_id=instance, estado="activo").exists()
        
        if usuarios_activos:
            instance.estado = "inactivo"
            instance.save()
            return Response(
                {"message":"El rol tiene usuarios activos, por lo que se ha desactivado"}, status = status.HTTP_200_OK
            )
        else:
            instance.delete()
            return Response({
                "message":"El rol no cuenta con usuarios activos, por lo cual se elimino"
            },status=status.HTTP_204_NO_CONTENT)
    
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
    