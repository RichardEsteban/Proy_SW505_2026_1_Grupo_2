from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


EstadoSolicitudReposicion = Literal[
    "ENVIADO",
    "EN_REVISION",
    "ACEPTADO",
    "EN_TRANSITO",
    "RECIBIDA",
    "RECHAZADA",
    "CANCELADA",
]


class SolicitudReposicionDetalleCreateRequest(BaseModel):
    idProducto: int
    cantidadSolicitada: int = Field(gt=0)


class SolicitudReposicionCreateRequest(BaseModel):
    idUbicacionOrigen: int | None = None
    idUbicacionDestino: int | None = None
    observacion: str | None = None
    detalles: list[SolicitudReposicionDetalleCreateRequest] = Field(min_length=1)


class SolicitudReposicionGestionRequest(BaseModel):
    observacion: str | None = None


class SolicitudReposicionDetalleResponse(BaseModel):
    idDetalleSolicitud: int
    idProducto: int
    codigoBarras: str
    nombreProducto: str
    cantidadSolicitada: int
    cantidadDespachada: int


class SolicitudReposicionResponse(BaseModel):
    idSolicitud: int
    idUbicacionOrigen: int
    ubicacionOrigen: str
    idUbicacionDestino: int
    ubicacionDestino: str
    idUsuarioSolicitante: int
    usuarioSolicitante: str
    idUsuarioDespachador: int | None
    usuarioDespachador: str | None
    idUsuarioReceptor: int | None
    usuarioReceptor: str | None
    fechaSolicitud: datetime
    fechaDespacho: datetime | None
    fechaRecepcion: datetime | None
    fechaAperturaRevision: datetime | None
    estado: EstadoSolicitudReposicion
    observacion: str | None
    detalles: list[SolicitudReposicionDetalleResponse]
