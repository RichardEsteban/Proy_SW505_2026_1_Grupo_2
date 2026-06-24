"""Entidades relacionadas a Ventas: Venta y DetalleVenta."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


class EstadoVenta(str, Enum):
    REGISTRADA = "REGISTRADA"
    ANULADA = "ANULADA"
    PAGADA = "PAGADA"


class TipoComprobante(str, Enum):
    BOLETA = "BOLETA"
    FACTURA = "FACTURA"
    TICKET = "TICKET"
    NOTA_VENTA = "NOTA_VENTA"


@dataclass
class DetalleVenta:
    id: Optional[int]
    venta_id: Optional[int]
    producto_id: int
    cantidad: float
    precio_unitario: float
    descuento: float = 0.0
    igv: float = 0.0
    subtotal: float = 0.0
    total: float = 0.0

    def calcular(self, igv_porcentaje: float = 18.0) -> None:
        bruto = self.cantidad * self.precio_unitario - self.descuento
        self.subtotal = round(bruto / (1 + igv_porcentaje / 100), 4)
        self.igv = round(bruto - self.subtotal, 4)
        self.total = round(bruto, 4)


@dataclass
class Venta:
    id: Optional[int]
    serie: str
    numero: str
    tipo_comprobante: TipoComprobante
    sucursal_id: int
    cliente_id: Optional[int]
    usuario_id: int
    fecha: datetime
    subtotal: float = 0.0
    igv: float = 0.0
    descuento_total: float = 0.0
    total: float = 0.0
    estado: EstadoVenta = EstadoVenta.REGISTRADA
    pdf_url: Optional[str] = None
    detalles: List[DetalleVenta] = field(default_factory=list)
    created_at: Optional[datetime] = None

    def calcular_totales(self, igv_porcentaje: float = 18.0) -> None:
        for d in self.detalles:
            d.calcular(igv_porcentaje)
        self.subtotal = round(sum(d.subtotal for d in self.detalles), 2)
        self.igv = round(sum(d.igv for d in self.detalles), 2)
        self.descuento_total = round(sum(d.descuento for d in self.detalles), 2)
        self.total = round(sum(d.total for d in self.detalles), 2)

    def anular(self) -> None:
        if self.estado == EstadoVenta.ANULADA:
            raise ValueError("La venta ya está anulada")
        self.estado = EstadoVenta.ANULADA
