"""Caso de uso: Consultar disponibilidad de stock."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from app.domain.entities.stock import TipoUbicacion


@dataclass
class DisponibilidadItem:
    producto_id: int
    sku: str
    nombre: str
    cantidad: float
    stock_minimo: float
    ubicacion_tipo: str
    ubicacion_id: int
    alerta_stock_bajo: bool


class ConsultarDisponibilidad:
    def __init__(self, repo_stock, repo_productos) -> None:
        self._stock = repo_stock
        self._productos = repo_productos

    def ejecutar(
        self,
        sucursal_id: int,
        termino: str = "",
        solo_bajo_minimo: bool = False,
    ) -> List[DisponibilidadItem]:
        stocks = self._stock.listar(
            ubicacion_tipo=TipoUbicacion.SUCURSAL,
            ubicacion_id=sucursal_id,
        )
        resultado: List[DisponibilidadItem] = []
        for st in stocks:
            prod = self._productos.obtener_por_id(st.producto_id)
            if prod is None:
                continue
            if termino and termino.lower() not in prod.nombre.lower() and termino not in prod.sku:
                continue
            alerta = st.requiere_reposicion
            if solo_bajo_minimo and not alerta:
                continue
            resultado.append(
                DisponibilidadItem(
                    producto_id=st.producto_id,
                    sku=prod.sku,
                    nombre=prod.nombre,
                    cantidad=st.cantidad,
                    stock_minimo=st.stock_minimo,
                    ubicacion_tipo=st.ubicacion_tipo.value,
                    ubicacion_id=st.ubicacion_id,
                    alerta_stock_bajo=alerta,
                )
            )
        return resultado
