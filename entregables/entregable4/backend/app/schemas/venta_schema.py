from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class VentaDetalleCreateRequest(BaseModel):
    idProducto: int
    cantidad: int = Field(gt=0)


class VentaCreateRequest(BaseModel):
    idMetodoPago: int
    idCliente: int | None = None
    idUbicacion: int | None = None
    detalles: list[VentaDetalleCreateRequest] = Field(min_length=1)


class VentaDetalleResponse(BaseModel):
    idDetalleVenta: int
    idProducto: int
    codigoBarras: str
    nombreProducto: str
    cantidad: int
    precioUnitarioFacturado: Decimal
    subtotal: Decimal
    igvAplicado: Decimal
    totalLinea: Decimal


class VentaResponse(BaseModel):
    idVenta: int
    idUbicacion: int
    ubicacion: str
    idUsuario: int
    usuario: str
    idCliente: int | None
    cliente: str | None
    idMetodoPago: int
    metodoPago: str
    fechaHora: datetime
    subtotalVenta: Decimal
    totalIgv: Decimal
    totalVenta: Decimal
    pdf_url: str | None
    detalles: list[VentaDetalleResponse]
