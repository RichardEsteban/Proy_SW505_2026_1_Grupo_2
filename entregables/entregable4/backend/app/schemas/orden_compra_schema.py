from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


EstadoOrdenCompra = Literal["SOLICITADO", "EN_TRANSITO", "RECIBIDO", "CANCELADO"]


class OrdenCompraDetalleCreateRequest(BaseModel):
    idProducto: int
    cantidadPedida: int = Field(gt=0)
    precioCompraUnitario: Decimal = Field(gt=0)


class OrdenCompraCreateRequest(BaseModel):
    idProveedor: int
    idUbicacionDestino: int | None = None
    detalles: list[OrdenCompraDetalleCreateRequest] = Field(min_length=1)


class OrdenCompraCancelarRequest(BaseModel):
    motivo: str | None = Field(default=None, max_length=255)


class OrdenCompraDetalleResponse(BaseModel):
    idDetalleOrden: int
    idProducto: int
    codigoBarras: str
    nombreProducto: str
    cantidadPedida: int
    cantidadRecibida: int
    precioCompraUnitario: Decimal
    subtotal: Decimal
    igvAplicado: Decimal
    totalLinea: Decimal


class OrdenCompraResponse(BaseModel):
    idOrdenCompra: int
    idProveedor: int
    proveedor: str
    idUbicacionDestino: int
    ubicacionDestino: str
    idUsuarioComprador: int
    usuarioComprador: str
    idUsuarioReceptor: int | None
    usuarioReceptor: str | None
    fechaPedido: datetime
    fechaRecepcion: datetime | None
    estado: EstadoOrdenCompra
    totalNeto: Decimal
    totalIgv: Decimal
    totalCompra: Decimal
    detalles: list[OrdenCompraDetalleResponse]
