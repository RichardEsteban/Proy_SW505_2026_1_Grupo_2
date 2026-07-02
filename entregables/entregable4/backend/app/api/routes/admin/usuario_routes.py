from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.constants import Roles
from app.core.dependencias import get_current_user
from app.core.permissions import require_roles
from app.db.session import get_db
from app.schemas.rol_schema import RolResponse
from app.schemas.usuario_schema import (
    CambiarContrasenaRequest,
    UsuarioCreateRequest,
    UsuarioResponse,
    UsuarioUpdateRequest,
)
from app.services.rol_service import RolService
from app.services.usuario_service import UsuarioService


router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)


@router.get(
    "",
    response_model=list[UsuarioResponse],
    dependencies=[Depends(require_roles(Roles.ADMIN))]
)
def listar_usuarios(
    incluir_inactivos: bool = Query(default=True),
    db: Session = Depends(get_db)
):
    return UsuarioService.listar(
        db=db,
        incluir_inactivos=incluir_inactivos
    )


@router.get(
    "/roles",
    response_model=list[RolResponse],
    dependencies=[Depends(require_roles(Roles.ADMIN))]
)
def listar_roles(db: Session = Depends(get_db)):
    return RolService.listar(db)


@router.get(
    "/{id_usuario}",
    response_model=UsuarioResponse,
    dependencies=[Depends(require_roles(Roles.ADMIN))]
)
def obtener_usuario(
    id_usuario: int,
    db: Session = Depends(get_db)
):
    return UsuarioService.obtener_por_id(db=db, id_usuario=id_usuario)


@router.post(
    "",
    response_model=UsuarioResponse,
    dependencies=[Depends(require_roles(Roles.ADMIN))]
)
def crear_usuario(
    datos: UsuarioCreateRequest,
    db: Session = Depends(get_db)
):
    return UsuarioService.crear(db=db, datos=datos)


@router.patch(
    "/{id_usuario}",
    response_model=UsuarioResponse
)
def actualizar_usuario(
    id_usuario: int,
    datos: UsuarioUpdateRequest,
    db: Session = Depends(get_db),
    usuario_actual=Depends(require_roles(Roles.ADMIN)),
):
    return UsuarioService.actualizar(
        db=db,
        id_usuario=id_usuario,
        datos=datos,
        usuario_actual=usuario_actual,
    )


@router.put("/me/contrasena")
def cambiar_mi_contrasena(
    datos: CambiarContrasenaRequest,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    return UsuarioService.cambiar_mi_contrasena(
        db=db,
        usuario_actual=usuario_actual,
        datos=datos,
    )
