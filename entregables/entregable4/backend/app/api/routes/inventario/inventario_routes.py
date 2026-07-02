from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.constants import Roles
from app.core.dependencias import get_current_user
from app.core.permissions import require_roles
from app.db.session import get_db
from app.schemas.inventario_schema import (
    InventarioCreateRequest,
    InventarioResponse,
    InventarioStockMinimoUpdateRequest,
    MovimientoInventarioCreateRequest,
    MovimientoInventarioResponse,
)
from app.services.inventario_service import InventarioService


router = APIRouter(
    prefix="/inventario",
    tags=["Inventario"]
)


@router.get("", response_model=list[InventarioResponse])
def listar_inventario(
    id_ubicacion: int | None = Query(default=None),
    id_producto: int | None = Query(default=None),
    solo_bajo_minimo: bool = Query(default=False),
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    return InventarioService.listar(
        db=db,
        usuario_actual=usuario_actual,
        id_ubicacion=id_ubicacion,
        id_producto=id_producto,
        solo_bajo_minimo=solo_bajo_minimo,
    )


@router.get("/ubicacion/{id_ubicacion}", response_model=list[InventarioResponse])
def listar_inventario_por_ubicacion(
    id_ubicacion: int,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    return InventarioService.listar(
        db=db,
        usuario_actual=usuario_actual,
        id_ubicacion=id_ubicacion,
    )


@router.get("/producto/{id_producto}", response_model=list[InventarioResponse])
def listar_inventario_por_producto(
    id_producto: int,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    return InventarioService.listar(
        db=db,
        usuario_actual=usuario_actual,
        id_producto=id_producto,
    )


@router.get("/movimientos", response_model=list[MovimientoInventarioResponse])
def listar_movimientos(
    id_ubicacion: int | None = Query(default=None),
    id_producto: int | None = Query(default=None),
    desde: datetime | None = Query(default=None),
    hasta: datetime | None = Query(default=None),
    limite: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    return InventarioService.listar_movimientos(
        db=db,
        usuario_actual=usuario_actual,
        id_ubicacion=id_ubicacion,
        id_producto=id_producto,
        desde=desde,
        hasta=hasta,
        limite=limite,
    )


@router.post(
    "/stock-inicial",
    response_model=InventarioResponse,
    dependencies=[Depends(require_roles(Roles.ADMIN, Roles.SUPERVISOR_ALMACEN))]
)
def crear_stock_inicial(
    datos: InventarioCreateRequest,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    return InventarioService.crear_stock_inicial(
        db=db,
        datos=datos,
        usuario_actual=usuario_actual,
    )


@router.post(
    "/movimientos",
    response_model=MovimientoInventarioResponse,
    dependencies=[Depends(require_roles(Roles.ADMIN, Roles.SUPERVISOR_ALMACEN))]
)
def registrar_movimiento(
    datos: MovimientoInventarioCreateRequest,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    return InventarioService.registrar_movimiento(
        db=db,
        datos=datos,
        usuario_actual=usuario_actual,
    )


@router.get("/{id_inventario}", response_model=InventarioResponse)
def obtener_inventario(
    id_inventario: int,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    return InventarioService.obtener_por_id(
        db=db,
        id_inventario=id_inventario,
        usuario_actual=usuario_actual,
    )


@router.patch(
    "/{id_inventario}/stock-minimo",
    response_model=InventarioResponse,
    dependencies=[Depends(require_roles(Roles.ADMIN, Roles.SUPERVISOR_ALMACEN, Roles.SUPERVISOR_SUCURSAL))]
)
def actualizar_stock_minimo(
    id_inventario: int,
    datos: InventarioStockMinimoUpdateRequest,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    return InventarioService.actualizar_stock_minimo(
        db=db,
        id_inventario=id_inventario,
        datos=datos,
        usuario_actual=usuario_actual,
    )
