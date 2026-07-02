from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.constants import Roles
from app.core.dependencias import get_current_user
from app.core.permissions import require_roles
from app.db.session import get_db
from app.schemas.producto_schema import (
    ProductoCreateRequest,
    ProductoResponse,
    ProductoUpdateRequest,
)
from app.services.producto_service import ProductoService


router = APIRouter(
    prefix="/productos",
    tags=["Productos"]
)


@router.get("", response_model=list[ProductoResponse])
def listar_productos(
    incluir_inactivos: bool = Query(default=False),
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    if usuario_actual.rol.nombreRol not in (Roles.ADMIN, Roles.SUPERVISOR_ALMACEN):
        incluir_inactivos = False

    return ProductoService.listar(
        db=db,
        incluir_inactivos=incluir_inactivos,
    )


@router.get("/codigo/{codigo_barras}", response_model=ProductoResponse)
def obtener_producto_por_codigo_barras(
    codigo_barras: str,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    return ProductoService.obtener_por_codigo_barras(
        db=db,
        codigo_barras=codigo_barras,
    )


@router.get("/{id_producto}", response_model=ProductoResponse)
def obtener_producto(
    id_producto: int,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    return ProductoService.obtener_por_id(db=db, id_producto=id_producto)


@router.post(
    "",
    response_model=ProductoResponse,
    dependencies=[Depends(require_roles(Roles.ADMIN, Roles.SUPERVISOR_ALMACEN))]
)
def crear_producto(
    datos: ProductoCreateRequest,
    db: Session = Depends(get_db),
):
    return ProductoService.crear(db=db, datos=datos)


@router.patch(
    "/{id_producto}",
    response_model=ProductoResponse,
    dependencies=[Depends(require_roles(Roles.ADMIN, Roles.SUPERVISOR_ALMACEN))]
)
def actualizar_producto(
    id_producto: int,
    datos: ProductoUpdateRequest,
    db: Session = Depends(get_db),
):
    return ProductoService.actualizar(
        db=db,
        id_producto=id_producto,
        datos=datos,
    )
