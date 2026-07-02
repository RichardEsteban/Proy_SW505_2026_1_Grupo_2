from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.constants import Roles
from app.core.permissions import require_roles
from app.db.session import get_db
from app.schemas.reporte_schema import (
    ReporteCompraResponse,
    ReporteKardexResponse,
    ReporteProductoVendidoResponse,
    ReporteReposicionPorEstadoResponse,
    ReporteResumenResponse,
    ReporteStockBajoResponse,
    ReporteVentaPorFechaResponse,
)
from app.services.reporte_service import ReporteService


ROLES_REPORTES = (Roles.ADMIN, Roles.SUPERVISOR_ALMACEN, Roles.SUPERVISOR_SUCURSAL, Roles.VENDEDOR)

router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.get("/resumen", response_model=ReporteResumenResponse, dependencies=[Depends(require_roles(*ROLES_REPORTES))])
def resumen(
    id_ubicacion: int | None = Query(default=None),
    desde: datetime | None = Query(default=None),
    hasta: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario_actual=Depends(require_roles(*ROLES_REPORTES)),
):
    return ReporteService.resumen(db, usuario_actual, id_ubicacion, desde, hasta)


@router.get("/ventas-por-fecha", response_model=list[ReporteVentaPorFechaResponse], dependencies=[Depends(require_roles(*ROLES_REPORTES))])
def ventas_por_fecha(
    id_ubicacion: int | None = Query(default=None),
    desde: datetime | None = Query(default=None),
    hasta: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario_actual=Depends(require_roles(*ROLES_REPORTES)),
):
    return ReporteService.ventas_por_fecha(db, usuario_actual, id_ubicacion, desde, hasta)


@router.get("/productos-mas-vendidos", response_model=list[ReporteProductoVendidoResponse], dependencies=[Depends(require_roles(*ROLES_REPORTES))])
def productos_mas_vendidos(
    id_ubicacion: int | None = Query(default=None),
    desde: datetime | None = Query(default=None),
    hasta: datetime | None = Query(default=None),
    limite: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    usuario_actual=Depends(require_roles(*ROLES_REPORTES)),
):
    return ReporteService.productos_mas_vendidos(db, usuario_actual, id_ubicacion, desde, hasta, limite)


@router.get("/stock-bajo", response_model=list[ReporteStockBajoResponse], dependencies=[Depends(require_roles(*ROLES_REPORTES))])
def stock_bajo(
    id_ubicacion: int | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario_actual=Depends(require_roles(*ROLES_REPORTES)),
):
    return ReporteService.stock_bajo(db, usuario_actual, id_ubicacion)


@router.get("/kardex", response_model=list[ReporteKardexResponse], dependencies=[Depends(require_roles(*ROLES_REPORTES))])
def kardex(
    id_ubicacion: int | None = Query(default=None),
    id_producto: int | None = Query(default=None),
    desde: datetime | None = Query(default=None),
    hasta: datetime | None = Query(default=None),
    limite: int = Query(default=200, ge=1, le=1000),
    db: Session = Depends(get_db),
    usuario_actual=Depends(require_roles(*ROLES_REPORTES)),
):
    return ReporteService.kardex(db, usuario_actual, id_ubicacion, id_producto, desde, hasta, limite)


@router.get("/compras", response_model=list[ReporteCompraResponse], dependencies=[Depends(require_roles(Roles.ADMIN, Roles.SUPERVISOR_ALMACEN))])
def compras(
    id_ubicacion: int | None = Query(default=None),
    estado: str | None = Query(default=None),
    desde: datetime | None = Query(default=None),
    hasta: datetime | None = Query(default=None),
    limite: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    usuario_actual=Depends(require_roles(Roles.ADMIN, Roles.SUPERVISOR_ALMACEN)),
):
    return ReporteService.compras(db, usuario_actual, id_ubicacion, estado, desde, hasta, limite)


@router.get("/reposiciones-por-estado", response_model=list[ReporteReposicionPorEstadoResponse], dependencies=[Depends(require_roles(Roles.ADMIN, Roles.SUPERVISOR_ALMACEN, Roles.SUPERVISOR_SUCURSAL))])
def reposiciones_por_estado(
    id_ubicacion_destino: int | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario_actual=Depends(require_roles(Roles.ADMIN, Roles.SUPERVISOR_ALMACEN, Roles.SUPERVISOR_SUCURSAL)),
):
    return ReporteService.reposiciones_por_estado(db, usuario_actual, id_ubicacion_destino)
