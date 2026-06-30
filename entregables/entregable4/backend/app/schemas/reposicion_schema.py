from pydantic import BaseModel
from typing import List


class DetalleReposicion(BaseModel):
    idProducto: int
    cantidadSolicitada: int


class ReposicionCreate(BaseModel):
    idUbicacionOrigen: int
    idUbicacionDestino: int
    idUsuarioSolicitante: int
    detalles: List[DetalleReposicion]


class ReposicionResponse(BaseModel):
    idSolicitud: int
    estado: str
    detalles: List[DetalleReposicion]

    class Config:
        from_attributes = True