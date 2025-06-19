from rol.models import Permiso_Rol

def obtener_permisos_usuario(usuario):
    """
    Obtiene los permisos de un usuario, devolviendo una lista con los modulos (permisos) que tiene el rol asignado."""
    
    if not usuario.rol_id:
        return []
    
    permisos = Permiso_Rol.objects.filter(rol_id=usuario.rol_id).select_related("permiso_id")
    modulos = [p.permiso_id.modulo for p in permisos if p.permiso_id and p.permiso_id.modulo]
    return modulos