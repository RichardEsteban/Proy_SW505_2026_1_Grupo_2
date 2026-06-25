"""Entidad Stock (StockSucursal / StockAlmacen)."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class TipoUbicacion(str, Enum):
    SUCURSAL = "SUCURSAL"
    ALMACEN = "ALMACEN"


@dataclass
class Stock:
    id: Optional[int]
    producto_id: int
    ubicacion_tipo: TipoUbicacion
    ubicacion_id: int
    cantidad: float
    stock_minimo: float = 0.0
    stock_maximo: Optional[float] = None
    updated_at: Optional[datetime] = None

    @property
    def requiere_reposicion(self) -> bool:
        return self.cantidad <= self.stock_minimo

    def descontar(self, cantidad: float) -> None:
        if cantidad <= 0:
            raise ValueError("Cantidad a descontar debe ser > 0")
        if self.cantidad < cantidad:
            raise ValueError(
                f"Stock insuficiente: disponible={self.cantidad}, requerido={cantidad}"
            )
        self.cantidad -= cantidad

    def incrementar(self, cantidad: float) -> None:
        if cantidad <= 0:
            raise ValueError("Cantidad a incrementar debe ser > 0")
        self.cantidad += cantidad
