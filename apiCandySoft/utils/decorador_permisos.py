from django.core.exceptions import PermissionDenied
from ..rol.models import Permiso_Rol

def verificar_permiso(permission_name):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            #obtener el rol del usuario que quiere entrar o hacer peticion
            usuario_rol = request.user.rol
            
            #comprobar si el rol tiene el modulo o permiso
            permiso = Permiso_Rol.objects.get(modulo=permission_name)
            tiene_permiso = Permiso_Rol.objects.filter(rol_id=usuario_rol, permiso_id=permiso).exists()
            
            if not tiene_permiso:
                raise PermissionDenied("No tienes permiso para acceder a esta modulo")
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator