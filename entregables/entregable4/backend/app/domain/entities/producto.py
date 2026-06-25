"""Entidad Producto."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Producto:
    id: Optional[int]
    sku: str
    codigo_barra: Optional[str]
    nombre: str
    descripcion: Optional[str]
    categoria_id: Optional[int]
    proveedor_id: Optional[int]
    precio_compra: float
    precio_venta: float
    incluye_igv: bool = True
    unidad_medida: str = "UND"
    imagen_url: Optional[str] = None
    activo: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def precio_sin_igv(self, igv_porcentaje: float = 18.0) -> float:
        if self.incluye_igv:
            return round(self.precio_venta / (1 + igv_porcentaje / 100), 4)
        return self.precio_venta

    def igv_unitario(self, igv_porcentaje: float = 18.0) -> float:
        return round(self.precio_venta - self.precio_sin_igv(igv_porcentaje), 4)
