from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.usuario import Usuario
from app.repositories.rol_repository import RolRepository
from app.repositories.ubicacion_repository import UbicacionRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.usuario_schema import (
    CambiarContrasenaRequest,
    UsuarioCreateRequest,
    UsuarioResponse,
    UsuarioUpdateRequest,
)
from app.utils.password import generar_hash_contrasena, verificar_contrasena


class UsuarioService:

    @staticmethod
    def _response(usuario: Usuario) -> UsuarioResponse:
        return UsuarioResponse(
            idUsuario=usuario.idUsuario,
            correoElectronico=usuario.correoElectronico,
            idRol=usuario.idRol,
            rol=usuario.rol.nombreRol,
            idUbicacion=usuario.idUbicacion,
            ubicacion=usuario.ubicacion.nombreUbicacion,
            tipoUbicacion=usuario.ubicacion.tipoUbicacion,
            isActivo=usuario.isActivo,
            isContrasenaTemporal=usuario.isContrasenaTemporal,
        )

    @staticmethod
    def listar(db: Session, incluir_inactivos: bool = True) -> list[UsuarioResponse]:
        usuarios = UsuarioRepository.obtener_todos(
            db=db,
            incluir_inactivos=incluir_inactivos
        )
        return [UsuarioService._response(usuario) for usuario in usuarios]

    @staticmethod
    def obtener_por_id(db: Session, id_usuario: int) -> UsuarioResponse:
        usuario = UsuarioRepository.obtener_por_id(db, id_usuario)

        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        return UsuarioService._response(usuario)

    @staticmethod
    def crear(db: Session, datos: UsuarioCreateRequest) -> UsuarioResponse:
        existente = UsuarioRepository.obtener_por_correo(
            db=db,
            correo=datos.correoElectronico
        )

        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un usuario con ese correo"
            )

        rol = RolRepository.obtener_por_id(db, datos.idRol)
        if not rol:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El rol indicado no existe"
            )

        ubicacion = UbicacionRepository.obtener_por_id(db, datos.idUbicacion)
        if not ubicacion:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La ubicación indicada no existe"
            )

        if not ubicacion.isActivo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puedes asignar usuarios a una ubicación inactiva"
            )

        usuario = Usuario(
            idUbicacion=datos.idUbicacion,
            idRol=datos.idRol,
            correoElectronico=datos.correoElectronico,
            contrasenaHash=generar_hash_contrasena(datos.contrasenaTemporal),
            isActivo=True,
            isContrasenaTemporal=True,
        )

        UsuarioRepository.guardar(db, usuario)
        db.commit()

        usuario_creado = UsuarioRepository.obtener_por_id(db, usuario.idUsuario)
        return UsuarioService._response(usuario_creado)

    @staticmethod
    def actualizar(
        db: Session,
        id_usuario: int,
        datos: UsuarioUpdateRequest,
        usuario_actual: Usuario,
    ) -> UsuarioResponse:
        usuario = UsuarioRepository.obtener_por_id(db, id_usuario)

        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        cambios = datos.model_dump(exclude_unset=True)

        if "correoElectronico" in cambios:
            existente = UsuarioRepository.obtener_por_correo(
                db=db,
                correo=cambios["correoElectronico"]
            )
            if existente and existente.idUsuario != id_usuario:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Ya existe otro usuario con ese correo"
                )

        if "idRol" in cambios:
            rol = RolRepository.obtener_por_id(db, cambios["idRol"])
            if not rol:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El rol indicado no existe"
                )

        if "idUbicacion" in cambios:
            ubicacion = UbicacionRepository.obtener_por_id(db, cambios["idUbicacion"])
            if not ubicacion:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La ubicación indicada no existe"
                )
            if not ubicacion.isActivo:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No puedes asignar usuarios a una ubicación inactiva"
                )

        if cambios.get("isActivo") is False and usuario.idUsuario == usuario_actual.idUsuario:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puedes desactivar tu propio usuario"
            )

        for campo, valor in cambios.items():
            setattr(usuario, campo, valor)

        UsuarioRepository.guardar(db, usuario)
        db.commit()

        usuario_actualizado = UsuarioRepository.obtener_por_id(db, id_usuario)
        return UsuarioService._response(usuario_actualizado)

    @staticmethod
    def cambiar_mi_contrasena(
        db: Session,
        usuario_actual: Usuario,
        datos: CambiarContrasenaRequest,
    ) -> dict[str, str]:
        usuario = UsuarioRepository.obtener_por_id(db, usuario_actual.idUsuario)

        if not verificar_contrasena(datos.contrasenaActual, usuario.contrasenaHash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña actual no es correcta"
            )

        if verificar_contrasena(datos.contrasenaNueva, usuario.contrasenaHash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La nueva contraseña no puede ser igual a la anterior"
            )

        usuario.contrasenaHash = generar_hash_contrasena(datos.contrasenaNueva)
        usuario.isContrasenaTemporal = False

        UsuarioRepository.guardar(db, usuario)
        db.commit()

        return {"mensaje": "Contraseña actualizada correctamente"}
