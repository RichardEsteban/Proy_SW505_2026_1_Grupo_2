from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.constants import Roles
from app.core.dependencias import get_current_user
from app.core.permissions import require_roles
from app.db.session import get_db
from app.schemas.categoria_schema import (
    CategoriaCreateRequest,
    CategoriaResponse,
    CategoriaUpdateRequest,
)
from app.services.categoria_service import CategoriaService


router = APIRouter(
    prefix="/categorias",
    tags=["Categorías"]
)


@router.get("", response_model=list[CategoriaResponse])
def listar_categorias(
    incluir_inactivas: bool = Query(default=False),
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    if usuario_actual.rol.nombreRol not in (Roles.ADMIN, Roles.SUPERVISOR_ALMACEN):
        incluir_inactivas = False

    return CategoriaService.listar(
        db=db,
        incluir_inactivas=incluir_inactivas,
    )


@router.get("/{id_categoria}", response_model=CategoriaResponse)
def obtener_categoria(
    id_categoria: int,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    return CategoriaService.obtener_por_id(db=db, id_categoria=id_categoria)


@router.post(
    "",
    response_model=CategoriaResponse,
    dependencies=[Depends(require_roles(Roles.ADMIN, Roles.SUPERVISOR_ALMACEN))]
)
def crear_categoria(
    datos: CategoriaCreateRequest,
    db: Session = Depends(get_db),
):
    return CategoriaService.crear(db=db, datos=datos)


@router.patch(
    "/{id_categoria}",
    response_model=CategoriaResponse,
    dependencies=[Depends(require_roles(Roles.ADMIN, Roles.SUPERVISOR_ALMACEN))]
)
def actualizar_categoria(
    id_categoria: int,
    datos: CategoriaUpdateRequest,
    db: Session = Depends(get_db),
):
    return CategoriaService.actualizar(
        db=db,
        id_categoria=id_categoria,
        datos=datos,
    )
