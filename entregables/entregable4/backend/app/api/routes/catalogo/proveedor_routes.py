from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.constants import Roles
from app.core.permissions import require_roles
from app.db.session import get_db
from app.schemas.proveedor_schema import (
    ProveedorCreateRequest,
    ProveedorResponse,
    ProveedorUpdateRequest,
)
from app.services.proveedor_service import ProveedorService


router = APIRouter(
    prefix="/proveedores",
    tags=["Proveedores"]
)


@router.get(
    "",
    response_model=list[ProveedorResponse],
    dependencies=[Depends(require_roles(Roles.ADMIN, Roles.SUPERVISOR_ALMACEN))]
)
def listar_proveedores(
    incluir_inactivos: bool = Query(default=True),
    db: Session = Depends(get_db),
):
    return ProveedorService.listar(
        db=db,
        incluir_inactivos=incluir_inactivos,
    )


@router.get(
    "/{id_proveedor}",
    response_model=ProveedorResponse,
    dependencies=[Depends(require_roles(Roles.ADMIN, Roles.SUPERVISOR_ALMACEN))]
)
def obtener_proveedor(
    id_proveedor: int,
    db: Session = Depends(get_db),
):
    return ProveedorService.obtener_por_id(db=db, id_proveedor=id_proveedor)


@router.post(
    "",
    response_model=ProveedorResponse,
    dependencies=[Depends(require_roles(Roles.ADMIN, Roles.SUPERVISOR_ALMACEN))]
)
def crear_proveedor(
    datos: ProveedorCreateRequest,
    db: Session = Depends(get_db),
):
    return ProveedorService.crear(db=db, datos=datos)


@router.patch(
    "/{id_proveedor}",
    response_model=ProveedorResponse,
    dependencies=[Depends(require_roles(Roles.ADMIN, Roles.SUPERVISOR_ALMACEN))]
)
def actualizar_proveedor(
    id_proveedor: int,
    datos: ProveedorUpdateRequest,
    db: Session = Depends(get_db),
):
    return ProveedorService.actualizar(
        db=db,
        id_proveedor=id_proveedor,
        datos=datos,
    )
