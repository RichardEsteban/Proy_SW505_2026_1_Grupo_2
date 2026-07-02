from datetime import datetime, date
from decimal import Decimal

from pydantic import BaseModel


class ReporteResumenResponse(BaseModel):
    totalVentas: Decimal
    cantidadVentas: int
    productosVendidos: int
    ticketPromedio: Decimal
    productosConStockBajo: int
    alertasPendientes: int
    ordenesCompraAbiertas: int
    reposicionesAbiertas: int


class ReporteVentaPorFechaResponse(BaseModel):
    fecha: date
    cantidadVentas: int
    subtotalVenta: Decimal
    totalIgv: Decimal
    totalVenta: Decimal


class ReporteProductoVendidoResponse(BaseModel):
    idProducto: int
    codigoBarras: str
    nombreProducto: str
    cantidadVendida: int
    totalVendido: Decimal


class ReporteStockBajoResponse(BaseModel):
    idInventario: int
    idUbicacion: int
    ubicacion: str
    idProducto: int
    codigoBarras: str
    producto: str
    stockDisponible: int
    stockMinimo: int
    estadoStock: str


class ReporteKardexResponse(BaseModel):
    idMovimiento: int
    fechaHora: datetime
    idUbicacion: int
    ubicacion: str
    idProducto: int
    producto: str
    usuario: str
    tipoMovimiento: str
    motivoMovimiento: str
    cantidad: int
    tipoReferencia: str | None
    idReferencia: int | None


class ReporteCompraResponse(BaseModel):
    idOrdenCompra: int
    proveedor: str
    ubicacionDestino: str
    usuarioComprador: str
    usuarioReceptor: str | None
    fechaPedido: datetime
    fechaRecepcion: datetime | None
    estado: str
    totalNeto: Decimal
    totalIgv: Decimal
    totalCompra: Decimal


class ReporteReposicionPorEstadoResponse(BaseModel):
    estado: str
    cantidad: int
