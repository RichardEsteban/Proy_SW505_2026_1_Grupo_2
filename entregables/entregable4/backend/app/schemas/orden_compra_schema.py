from pydantic import BaseModel
from typing import List


class DetalleOrdenCompra(BaseModel):
    idProducto: int
    cantidadPedida: int
    precioCompraUnitario: float


class OrdenCompraCreate(BaseModel):
    idProveedor: int
    idUbicacionDestino: int
    idUsuarioComprador: int
    detalles: List[DetalleOrdenCompra]


class OrdenCompraResponse(BaseModel):
    idOrdenCompra: int
    estado: str
    totalCompra: float
    detalles: List[DetalleOrdenCompra]

    class Config:
        from_attributes = True