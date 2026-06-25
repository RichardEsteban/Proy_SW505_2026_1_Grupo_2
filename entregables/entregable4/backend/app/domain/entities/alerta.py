"""Entidades de Alerta de stock."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class TipoAlerta(str, Enum):
    STOCK_BAJO = "STOCK_BAJO"
    STOCK_AGOTADO = "STOCK_AGOTADO"
    SOBRESTOCK = "SOBRESTOCK"
    VENCIMIENTO = "VENCIMIENTO"


class EstadoAlerta(str, Enum):
    ACTIVA = "ACTIVA"
    ATENDIDA = "ATENDIDA"
    DESCARTADA = "DESCARTADA"


@dataclass
class Alerta:
    id: Optional[int]
    tipo: TipoAlerta
    producto_id: int
    ubicacion_tipo: str
    ubicacion_id: int
    cantidad_actual: float
    stock_referencia: float
    estado: EstadoAlerta = EstadoAlerta.ACTIVA
    mensaje: str = ""
    created_at: Optional[datetime] = None
    atendida_at: Optional[datetime] = None

    def atender(self) -> None:
        self.estado = EstadoAlerta.ATENDIDA
        self.atendida_at = datetime.utcnow()

    def descartar(self) -> None:
        self.estado = EstadoAlerta.DESCARTADA
        self.atendida_at = datetime.utcnow()
