from rest_framework import viewsets, status;
from rest_framework.response import Response;
from rest_framework.decorators import action;
from rest_framework.permissions import AllowAny;

from ..models import Rol
from ..models import Permiso_Rol
from ..serializers import RolSerializer
from ..serializers import PermisoRolSerializer
from usuario.models.usuario import Usuario

from permisos.custom_permissions import TienePermisoModulo



class RolViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all();
    serializer_class = RolSerializer;
    permission_classes = [TienePermisoModulo("Rol")];
    
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
    def cambiar_estado(self, request, pk=None):
        rol = self.get_object()
        nuevo_estado = "Activo" if rol.estado == "Inactivo" else "Inactivo"

        # Actualiza el rol
        rol.estado = nuevo_estado
        rol.save()

        # Actualiza el estado de todos los usuarios con ese rol
        Usuario.objects.filter(rol_id=rol.id).update(estado=nuevo_estado)

        serializer = self.get_serializer(rol)
        return Response({
            "message": f"El estado del rol cambió a {nuevo_estado} correctamente",
            "data": serializer.data
        })
    
    #cambiar el eliminar (destroy en django para inactivo)
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object();

        usuarios_activos = Usuario.objects.filter(rol_id=instance, estado="Activo").exists()
        
        if usuarios_activos:
            instance.estado = "Inactivo"
            instance.save()
            usuarios_activo = Usuario.objects.filter(rol_id=instance).update(estado="Inactivo")
            return Response(
                {"message":"El rol tiene usuarios activos, por lo que se ha desactivado"}, status = status.HTTP_200_OK
            )
        else:
            instance.delete()
            usuarios_activos.delete()
            return Response({
                "message":"El rol no cuenta con usuarios activos, por lo cual se elimino"
            },status=status.HTTP_204_NO_CONTENT)
    
    #filtrar roles por estado
    @action(detail=False,methods=['get'])
    def activos(self,request):
        roles_activos = Rol.objects.filter(estado="Activo");
        serializer = self.get_serializer(roles_activos, many=True);
        return Response(serializer.data);
    
    @action(detail=False,methods=["get"])
    def inactivos(self,request):
        roles_inactivos = Rol.objects.filter(estado="Inactivo");
        serializer = self.get_serializer(roles_inactivos, many=True);
        return Response(serializer.data);