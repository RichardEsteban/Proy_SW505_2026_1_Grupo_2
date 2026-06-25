"""Caso de uso: Generar solicitud de reposición (sucursal -> almacén)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List
import uuid

from app.application.ports.repositorio_solicitud import RepositorioSolicitud
from app.domain.entities.solicitud import DetalleSolicitud, SolicitudReposicion
from app.domain.entities.stock import TipoUbicacion


@dataclass
class ItemSolicitudInput:
    producto_id: int
    cantidad: float


@dataclass
class SolicitudInput:
    sucursal_origen_id: int
    almacen_destino_id: int
    usuario_solicita_id: int
    items: List[ItemSolicitudInput]
    motivo: str | None = None


class GenerarSolicitud:
    def __init__(self, repo_solicitudes: RepositorioSolicitud, repo_stock) -> None:
        self._solicitudes = repo_solicitudes
        self._stock = repo_stock

    def ejecutar(self, data: SolicitudInput) -> SolicitudReposicion:
        detalles = [
            DetalleSolicitud(
                id=None,
                solicitud_id=None,
                producto_id=item.producto_id,
                cantidad_solicitada=item.cantidad,
            )
            for item in data.items
        ]
        codigo = f"SOL-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        solicitud = SolicitudReposicion(
            id=None,
            codigo=codigo,
            sucursal_origen_id=data.sucursal_origen_id,
            almacen_destino_id=data.almacen_destino_id,
            usuario_solicita_id=data.usuario_solicita_id,
            motivo=data.motivo,
            fecha_solicitud=datetime.utcnow(),
            detalles=detalles,
        )
        return self._solicitudes.crear(solicitud)
