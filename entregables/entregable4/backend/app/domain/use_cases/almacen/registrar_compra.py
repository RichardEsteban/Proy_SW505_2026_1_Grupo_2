"""Caso de uso: Registrar compra a proveedor (entrada desde factura)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List

from app.domain.entities.stock import TipoUbicacion


@dataclass
class ItemCompra:
    producto_id: int
    cantidad: float
    precio_compra: float


@dataclass
class CompraInput:
    proveedor_id: int
    almacen_id: int
    numero_factura: str
    items: List[ItemCompra]
    igv_porcentaje: float = 18.0


class RegistrarCompra:
    def __init__(self, repo_stock, repo_proveedores, repo_compras, uow=None) -> None:
        self._stock = repo_stock
        self._proveedores = repo_proveedores
        self._compras = repo_compras
        self._uow = uow

    def ejecutar(self, data: CompraInput) -> dict:
        proveedor = self._proveedores.obtener_por_id(data.proveedor_id)
        if proveedor is None:
            raise ValueError(f"Proveedor {data.proveedor_id} no existe")

        total = 0.0
        for it in data.items:
            total += it.cantidad * it.precio_compra
        igv = round(total * data.igv_porcentaje / 100, 2)
        total_con_igv = round(total + igv, 2)

        compra_id = self._compras.crear(
            {
                "proveedor_id": data.proveedor_id,
                "almacen_id": data.almacen_id,
                "numero_factura": data.numero_factura,
                "subtotal": round(total, 2),
                "igv": igv,
                "total": total_con_igv,
                "fecha": datetime.utcnow(),
            }
        )

        # Incrementar stock
        for it in data.items:
            stock = self._stock.obtener(
                producto_id=it.producto_id,
                ubicacion_tipo=TipoUbicacion.ALMACEN,
                ubicacion_id=data.almacen_id,
            )
            if stock is None:
                from app.domain.entities.stock import Stock

                stock = Stock(
                    id=None,
                    producto_id=it.producto_id,
                    ubicacion_tipo=TipoUbicacion.ALMACEN,
                    ubicacion_id=data.almacen_id,
                    cantidad=0.0,
                )
                stock = self._stock.crear(stock)
            stock.incrementar(it.cantidad)
            self._stock.actualizar(stock)

        return {
            "compra_id": compra_id,
            "subtotal": round(total, 2),
            "igv": igv,
            "total": total_con_igv,
        }
