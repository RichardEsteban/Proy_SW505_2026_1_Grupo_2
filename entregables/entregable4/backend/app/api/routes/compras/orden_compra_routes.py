from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.constants import Roles
from app.core.permissions import require_roles
from app.db.session import get_db
from app.schemas.orden_compra_schema import (
    EstadoOrdenCompra,
    OrdenCompraCancelarRequest,
    OrdenCompraCreateRequest,
    OrdenCompraResponse,
)
from app.services.compra_service import CompraService


router = APIRouter(prefix="/ordenes-compra", tags=["Órdenes de compra"])


@router.get("", response_model=list[OrdenCompraResponse], dependencies=[Depends(require_roles(Roles.ADMIN, Roles.SUPERVISOR_ALMACEN))])
def listar_ordenes_compra(
    id_proveedor: int | None = Query(default=None),
    id_ubicacion_destino: int | None = Query(default=None),
    estado: EstadoOrdenCompra | None = Query(default=None),
    desde: datetime | None = Query(default=None),
    hasta: datetime | None = Query(default=None),
    limite: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return CompraService.listar(db, id_proveedor, id_ubicacion_destino, estado, desde, hasta, limite)


@router.post("", response_model=OrdenCompraResponse, dependencies=[Depends(require_roles(Roles.ADMIN))])
def crear_orden_compra(
    datos: OrdenCompraCreateRequest,
    db: Session = Depends(get_db),
    usuario_actual=Depends(require_roles(Roles.ADMIN)),
):
    return CompraService.crear(db=db, datos=datos, usuario_actual=usuario_actual)


@router.get("/{id_orden_compra}", response_model=OrdenCompraResponse, dependencies=[Depends(require_roles(Roles.ADMIN, Roles.SUPERVISOR_ALMACEN))])
def obtener_orden_compra(id_orden_compra: int, db: Session = Depends(get_db)):
    return CompraService.obtener_por_id(db=db, id_orden_compra=id_orden_compra)


@router.patch("/{id_orden_compra}/enviar", response_model=OrdenCompraResponse, dependencies=[Depends(require_roles(Roles.ADMIN))])
def enviar_orden_compra(
    id_orden_compra: int,
    db: Session = Depends(get_db),
    usuario_actual=Depends(require_roles(Roles.ADMIN)),
):
    return CompraService.enviar(db=db, id_orden_compra=id_orden_compra, usuario_actual=usuario_actual)


@router.patch("/{id_orden_compra}/recibir", response_model=OrdenCompraResponse, dependencies=[Depends(require_roles(Roles.SUPERVISOR_ALMACEN))])
def recibir_orden_compra(
    id_orden_compra: int,
    db: Session = Depends(get_db),
    usuario_actual=Depends(require_roles(Roles.SUPERVISOR_ALMACEN)),
):
    return CompraService.recibir(db=db, id_orden_compra=id_orden_compra, usuario_actual=usuario_actual)


@router.patch("/{id_orden_compra}/cancelar", response_model=OrdenCompraResponse, dependencies=[Depends(require_roles(Roles.ADMIN))])
def cancelar_orden_compra(
    id_orden_compra: int,
    datos: OrdenCompraCancelarRequest | None = None,
    db: Session = Depends(get_db),
    usuario_actual=Depends(require_roles(Roles.ADMIN)),
):
    return CompraService.cancelar(db=db, id_orden_compra=id_orden_compra, datos=datos or OrdenCompraCancelarRequest(), usuario_actual=usuario_actual)


@router.patch("/{id_orden_compra}/anular", response_model=OrdenCompraResponse, dependencies=[Depends(require_roles(Roles.ADMIN))])
def anular_orden_compra(
    id_orden_compra: int,
    datos: OrdenCompraCancelarRequest | None = None,
    db: Session = Depends(get_db),
    usuario_actual=Depends(require_roles(Roles.ADMIN)),
):
    return CompraService.cancelar(db=db, id_orden_compra=id_orden_compra, datos=datos or OrdenCompraCancelarRequest(), usuario_actual=usuario_actual)
