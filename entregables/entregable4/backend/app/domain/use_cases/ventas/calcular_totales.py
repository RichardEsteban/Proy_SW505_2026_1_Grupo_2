"""Caso de uso: Calcular totales de una venta (preview antes de registrar)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from app.domain.entities.venta import DetalleVenta


@dataclass
class ItemCalculo:
    cantidad: float
    precio_unitario: float
    descuento: float = 0.0


@dataclass
class ResultadoCalculo:
    subtotal: float
    igv: float
    descuento_total: float
    total: float
    detalle: List[dict]


class CalcularTotales:
    def __init__(self, igv_porcentaje: float = 18.0) -> None:
        self.igv = igv_porcentaje

    def ejecutar(self, items: List[ItemCalculo]) -> ResultadoCalculo:
        detalles: List[dict] = []
        subtotal = 0.0
        igv_total = 0.0
        descuento_total = 0.0
        total = 0.0

        for it in items:
            d = DetalleVenta(
                id=None,
                venta_id=None,
                producto_id=0,
                cantidad=it.cantidad,
                precio_unitario=it.precio_unitario,
                descuento=it.descuento,
            )
            d.calcular(self.igv)
            subtotal += d.subtotal
            igv_total += d.igv
            descuento_total += d.descuento
            total += d.total
            detalles.append(
                {
                    "cantidad": d.cantidad,
                    "precio_unitario": d.precio_unitario,
                    "descuento": d.descuento,
                    "subtotal": d.subtotal,
                    "igv": d.igv,
                    "total": d.total,
                }
            )

        return ResultadoCalculo(
            subtotal=round(subtotal, 2),
            igv=round(igv_total, 2),
            descuento_total=round(descuento_total, 2),
            total=round(total, 2),
            detalle=detalles,
        )
