"""Entidad Solicitud de reposición y su Detalle."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


class EstadoSolicitud(str, Enum):
    """Máquina de estados de una solicitud de reposición."""
    PENDIENTE = "PENDIENTE"
    APROBADA = "APROBADA"
    EN_TRANSITO = "EN_TRANSITO"
    RECIBIDA = "RECIBIDA"
    RECHAZADA = "RECHAZADA"
    CANCELADA = "CANCELADA"


# Transiciones válidas
TRANSICIONES_VALIDAS: dict[EstadoSolicitud, set[EstadoSolicitud]] = {
    EstadoSolicitud.PENDIENTE: {EstadoSolicitud.APROBADA, EstadoSolicitud.RECHAZADA, EstadoSolicitud.CANCELADA},
    EstadoSolicitud.APROBADA: {EstadoSolicitud.EN_TRANSITO, EstadoSolicitud.CANCELADA},
    EstadoSolicitud.EN_TRANSITO: {EstadoSolicitud.RECIBIDA},
    EstadoSolicitud.RECIBIDA: set(),
    EstadoSolicitud.RECHAZADA: set(),
    EstadoSolicitud.CANCELADA: set(),
}


@dataclass
class DetalleSolicitud:
    id: Optional[int]
    solicitud_id: Optional[int]
    producto_id: int
    cantidad_solicitada: float
    cantidad_enviada: float = 0.0
    cantidad_recibida: float = 0.0


@dataclass
class SolicitudReposicion:
    id: Optional[int]
    codigo: str
    sucursal_origen_id: int
    almacen_destino_id: int
    usuario_solicita_id: int
    usuario_evalua_id: Optional[int] = None
    estado: EstadoSolicitud = EstadoSolicitud.PENDIENTE
    motivo: Optional[str] = None
    observacion: Optional[str] = None
    fecha_solicitud: Optional[datetime] = None
    fecha_evaluacion: Optional[datetime] = None
    fecha_envio: Optional[datetime] = None
    fecha_recepcion: Optional[datetime] = None
    detalles: List[DetalleSolicitud] = field(default_factory=list)

    def transicionar(self, nuevo: EstadoSolicitud) -> None:
        """Aplica máquina de estados. Lanza ValueError si la transición no es válida."""
        if nuevo not in TRANSICIONES_VALIDAS.get(self.estado, set()):
            raise ValueError(
                f"Transición inválida: {self.estado.value} -> {nuevo.value}"
            )
        self.estado = nuevo

    def aprobar(self, evaluador_id: int) -> None:
        self.transicionar(EstadoSolicitud.APROBADA)
        self.usuario_evalua_id = evaluador_id
        self.fecha_evaluacion = datetime.utcnow()

    def rechazar(self, evaluador_id: int, motivo: str) -> None:
        self.transicionar(EstadoSolicitud.RECHAZADA)
        self.usuario_evalua_id = evaluador_id
        self.observacion = motivo
        self.fecha_evaluacion = datetime.utcnow()

    def enviar(self) -> None:
        self.transicionar(EstadoSolicitud.EN_TRANSITO)
        self.fecha_envio = datetime.utcnow()

    def recibir(self) -> None:
        self.transicionar(EstadoSolicitud.RECIBIDA)
        self.fecha_recepcion = datetime.utcnow()
