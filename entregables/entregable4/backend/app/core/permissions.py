from collections.abc import Callable

from fastapi import Depends, HTTPException, status

from app.core.dependencias import get_current_user


def require_roles(*roles_permitidos: str) -> Callable:
    """
    Dependencia reutilizable para proteger rutas por rol.

    Uso:
        usuario = Depends(require_roles("ADMIN"))
    """

    def _verificar_rol(usuario=Depends(get_current_user)):
        nombre_rol = usuario.rol.nombreRol

        if nombre_rol not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para realizar esta acción"
            )

        return usuario

    return _verificar_rol
