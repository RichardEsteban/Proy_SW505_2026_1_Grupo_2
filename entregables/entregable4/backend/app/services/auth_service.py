from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.auth_schema import LoginRequest, TokenResponse, UsuarioAuthResponse
from app.utils.jwt import crear_access_token
from app.utils.password import verificar_contrasena


class AuthService:

    @staticmethod
    def _crear_usuario_response(usuario) -> UsuarioAuthResponse:
        return UsuarioAuthResponse(
            idUsuario=usuario.idUsuario,
            correoElectronico=usuario.correoElectronico,
            idRol=usuario.idRol,
            rol=usuario.rol.nombreRol,
            idUbicacion=usuario.idUbicacion,
            ubicacion=usuario.ubicacion.nombreUbicacion,
            tipoUbicacion=usuario.ubicacion.tipoUbicacion,
            isContrasenaTemporal=usuario.isContrasenaTemporal
        )

    @staticmethod
    def login(db: Session, datos: LoginRequest) -> TokenResponse:
        usuario = UsuarioRepository.obtener_por_correo(
            db=db,
            correo=datos.correoElectronico
        )

        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas"
            )

        if not verificar_contrasena(datos.contrasena, usuario.contrasenaHash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas"
            )

        if not usuario.isActivo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El usuario está inactivo"
            )

        access_token = crear_access_token({
            "sub": str(usuario.idUsuario),
            "correo": usuario.correoElectronico,
            "rol": usuario.rol.nombreRol,
            "idRol": usuario.idRol,
            "idUbicacion": usuario.idUbicacion,
            "tipoUbicacion": usuario.ubicacion.tipoUbicacion
        })

        return TokenResponse(
            access_token=access_token,
            usuario=AuthService._crear_usuario_response(usuario)
        )