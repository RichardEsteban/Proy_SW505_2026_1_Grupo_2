"""Caso de uso: Registrar entrada manual a almacén (ajuste, devolución)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from app.domain.entities.stock import Stock, TipoUbicacion


@dataclass
class ItemEntrada:
    producto_id: int
    cantidad: float
    stock_minimo: float = 0.0


@dataclass
class EntradaInput:
    almacen_id: int
    items: List[ItemEntrada]
    observacion: str | None = None


class RegistrarEntrada:
    def __init__(self, repo_stock, uow=None) -> None:
        self._stock = repo_stock
        self._uow = uow

    def ejecutar(self, data: EntradaInput) -> int:
        """Retorna el número de items procesados."""
        procesados = 0
        with self._uow() as uow:
            for it in data.items:
                stock = self._stock.obtener(
                    producto_id=it.producto_id,
                    ubicacion_tipo=TipoUbicacion.ALMACEN,
                    ubicacion_id=data.almacen_id,
                )
                if stock is None:
                    stock = Stock(
                        id=None,
                        producto_id=it.producto_id,
                        ubicacion_tipo=TipoUbicacion.ALMACEN,
                        ubicacion_id=data.almacen_id,
                        cantidad=0.0,
                        stock_minimo=it.stock_minimo,
                    )
                    stock = self._stock.crear(stock)
                stock.incrementar(it.cantidad)
                self._stock.actualizar(stock)
                procesados += 1
            uow.commit()
        return procesados
