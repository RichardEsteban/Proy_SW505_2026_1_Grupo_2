from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.models.sesion_usuario import SesionUsuario
from app.repositories.usuario_repository import UsuarioRepository
from app.utils.jwt import decodificar_token


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    payload = decodificar_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )

    id_usuario = payload.get("sub")
    token_id = payload.get("sid")

    if id_usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

    if token_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión inválida. Inicia sesión nuevamente."
        )

    usuario = UsuarioRepository.obtener_por_id(
        db=db,
        id_usuario=int(id_usuario)
    )

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )

    if not usuario.isActivo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario está inactivo"
        )

    sesion = db.query(SesionUsuario).filter(
        SesionUsuario.idUsuario == usuario.idUsuario,
        SesionUsuario.tokenId == token_id,
        SesionUsuario.isActiva == True,  # noqa: E712
    ).first()

    if sesion is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="La sesión ya no está activa. Inicia sesión nuevamente."
        )

    settings = get_settings()
    ahora = datetime.utcnow()
    limite = ahora - timedelta(minutes=settings.session_inactivity_minutes)

    if sesion.fechaUltimaActividad < limite:
        sesion.isActiva = False
        sesion.fechaCierre = ahora
        sesion.motivoCierre = "INACTIVIDAD"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión expirada por inactividad. Inicia sesión nuevamente."
        )

    # Cada request autenticado actualiza la actividad; el heartbeat del frontend usa este mismo flujo.
    sesion.fechaUltimaActividad = ahora
    db.commit()
    db.refresh(usuario)

    return usuario
