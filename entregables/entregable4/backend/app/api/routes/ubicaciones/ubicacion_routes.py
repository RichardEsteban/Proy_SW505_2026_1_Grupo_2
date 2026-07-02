from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.constants import Roles
from app.core.permissions import require_roles
from app.db.session import get_db
from app.schemas.ubicacion_schema import (
    UbicacionCreateRequest,
    UbicacionResponse,
    UbicacionUpdateRequest,
)
from app.services.ubicacion_service import UbicacionService


router = APIRouter(
    prefix="/ubicaciones",
    tags=["Ubicaciones"]
)


@router.get(
    "",
    response_model=list[UbicacionResponse],
    dependencies=[Depends(require_roles(Roles.ADMIN, Roles.SUPERVISOR_ALMACEN))]
)
def listar_ubicaciones(
    incluir_inactivas: bool = Query(default=True),
    db: Session = Depends(get_db)
):
    return UbicacionService.listar(
        db=db,
        incluir_inactivas=incluir_inactivas
    )


@router.get(
    "/{id_ubicacion}",
    response_model=UbicacionResponse,
    dependencies=[Depends(require_roles(Roles.ADMIN, Roles.SUPERVISOR_ALMACEN))]
)
def obtener_ubicacion(
    id_ubicacion: int,
    db: Session = Depends(get_db)
):
    return UbicacionService.obtener_por_id(db=db, id_ubicacion=id_ubicacion)


@router.post(
    "",
    response_model=UbicacionResponse,
    dependencies=[Depends(require_roles(Roles.ADMIN))]
)
def crear_ubicacion(
    datos: UbicacionCreateRequest,
    db: Session = Depends(get_db)
):
    return UbicacionService.crear(db=db, datos=datos)


@router.patch(
    "/{id_ubicacion}",
    response_model=UbicacionResponse,
    dependencies=[Depends(require_roles(Roles.ADMIN))]
)
def actualizar_ubicacion(
    id_ubicacion: int,
    datos: UbicacionUpdateRequest,
    db: Session = Depends(get_db)
):
    return UbicacionService.actualizar(
        db=db,
        id_ubicacion=id_ubicacion,
        datos=datos
    )
