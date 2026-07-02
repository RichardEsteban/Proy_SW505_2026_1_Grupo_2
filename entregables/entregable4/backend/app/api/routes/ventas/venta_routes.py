from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.constants import Roles
from app.core.dependencias import get_current_user
from app.core.permissions import require_roles
from app.db.session import get_db
from app.schemas.venta_schema import VentaCreateRequest, VentaResponse
from app.services.venta_service import VentaService


router = APIRouter(
    prefix="/ventas",
    tags=["Ventas"]
)


@router.get("", response_model=list[VentaResponse])
def listar_ventas(
    id_ubicacion: int | None = Query(default=None),
    id_usuario: int | None = Query(default=None),
    desde: datetime | None = Query(default=None),
    hasta: datetime | None = Query(default=None),
    limite: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    return VentaService.listar(
        db=db,
        usuario_actual=usuario_actual,
        id_ubicacion=id_ubicacion,
        id_usuario=id_usuario,
        desde=desde,
        hasta=hasta,
        limite=limite,
    )


@router.post(
    "",
    response_model=VentaResponse,
    dependencies=[Depends(require_roles(Roles.ADMIN, Roles.VENDEDOR, Roles.SUPERVISOR_SUCURSAL))]
)
def crear_venta(
    datos: VentaCreateRequest,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    return VentaService.crear(db=db, datos=datos, usuario_actual=usuario_actual)


@router.get("/{id_venta}", response_model=VentaResponse)
def obtener_venta(
    id_venta: int,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    return VentaService.obtener_por_id(db=db, id_venta=id_venta, usuario_actual=usuario_actual)
