from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


TipoMovimiento = Literal["INGRESO", "SALIDA"]
MotivoMovimiento = Literal[
    "VENTA",
    "COMPRA_PROVEEDOR",
    "REPOSICION_ENVIADA",
    "REPOSICION_RECIBIDA",
    "MERMA",
    "AJUSTE",
]
TipoReferencia = Literal["VENTA", "ORDEN_COMPRA", "SOLICITUD_REPOSICION"]
EstadoStock = Literal["NORMAL", "STOCK_MINIMO", "STOCK_AGOTADO"]


class InventarioCreateRequest(BaseModel):
    idUbicacion: int
    idProducto: int
    stockDisponible: int = Field(default=0, ge=0)
    stockMinimo: int = Field(default=0, ge=0)


class InventarioStockMinimoUpdateRequest(BaseModel):
    stockMinimo: int = Field(ge=0)


class MovimientoInventarioCreateRequest(BaseModel):
    idUbicacion: int
    idProducto: int
    cantidad: int = Field(gt=0)
    tipoMovimiento: TipoMovimiento
    motivoMovimiento: MotivoMovimiento = "AJUSTE"
    tipoReferencia: TipoReferencia | None = None
    idReferencia: int | None = None


class InventarioResponse(BaseModel):
    idInventario: int
    idUbicacion: int
    ubicacion: str
    tipoUbicacion: str
    idProducto: int
    codigoBarras: str
    producto: str
    categoria: str | None
    stockDisponible: int
    stockMinimo: int
    estadoStock: EstadoStock


class MovimientoInventarioResponse(BaseModel):
    idMovimiento: int
    idUbicacion: int
    ubicacion: str
    idProducto: int
    producto: str
    idUsuario: int
    usuario: str
    cantidad: int
    tipoMovimiento: str
    motivoMovimiento: str
    tipoReferencia: str | None
    idReferencia: int | None
    fechaHora: datetime
