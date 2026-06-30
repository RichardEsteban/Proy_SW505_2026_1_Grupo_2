from pydantic import BaseModel
from typing import List
from datetime import datetime


class DetalleVenta(BaseModel):
    idProducto: int
    cantidad: int
    precioUnitarioFacturado: float


class VentaCreate(BaseModel):
    idUbicacion: int
    idUsuario: int
    idCliente: int | None
    idMetodoPago: int
    detalles: List[DetalleVenta]


class VentaResponse(BaseModel):
    idVenta: int
    fechaHora: datetime
    totalVenta: float
    detalles: List[DetalleVenta]

    class Config:
        from_attributes = True