# permisos/custom_permissions.py

from rest_framework.permissions import BasePermission
from utils.permisos import obtener_permisos_usuario

def TienePermisoModulo(modulo_requerido):
    class _PermisoModulo(BasePermission):
        def has_permission(self, request, view):
            usuario = request.user
            if not usuario.is_authenticated:
                return False

            permisos = getattr(usuario, 'permisos_cache', None)
            if permisos is None:
                permisos = obtener_permisos_usuario(usuario)
                usuario.permisos_cache = permisos

            return modulo_requerido in permisos
    return _PermisoModulo
