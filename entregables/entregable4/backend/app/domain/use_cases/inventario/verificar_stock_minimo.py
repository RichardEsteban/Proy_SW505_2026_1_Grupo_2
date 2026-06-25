"""Caso de uso: Verificar stock mínimo y emitir alertas."""
from __future__ import annotations

from typing import List

from app.application.ports.repositorio_alerta import RepositorioAlerta
from app.domain.entities.alerta import Alerta, EstadoAlerta, TipoAlerta
from app.domain.entities.stock import TipoUbicacion


class VerificarStockMinimo:
    """Recorre el stock de una/sucursal y crea Alertas para los productos
    cuya cantidad <= stock_minimo."""

    def __init__(
        self, repo_stock, repo_productos, repo_alertas: RepositorioAlerta
    ) -> None:
        self._stock = repo_stock
        self._productos = repo_productos
        self._alertas = repo_alertas

    def ejecutar(self, sucursal_id: int) -> List[Alerta]:
        creadas: List[Alerta] = []
        stocks = self._stock.listar(
            ubicacion_tipo=TipoUbicacion.SUCURSAL, ubicacion_id=sucursal_id
        )
        for st in stocks:
            if not st.requiere_reposicion:
                continue
            # Verificar si ya hay alerta activa
            existentes = self._alertas.listar(
                estado=EstadoAlerta.ACTIVA,
                ubicacion_id=st.ubicacion_id,
            )
            if any(
                a.producto_id == st.producto_id
                and a.ubicacion_id == st.ubicacion_id
                for a in existentes
            ):
                continue
            tipo = (
                TipoAlerta.STOCK_AGOTADO
                if st.cantidad <= 0
                else TipoAlerta.STOCK_BAJO
            )
            prod = self._productos.obtener_por_id(st.producto_id)
            nombre = prod.nombre if prod else f"Producto {st.producto_id}"
            alerta = Alerta(
                id=None,
                tipo=tipo,
                producto_id=st.producto_id,
                ubicacion_tipo=st.ubicacion_tipo.value,
                ubicacion_id=st.ubicacion_id,
                cantidad_actual=st.cantidad,
                stock_referencia=st.stock_minimo,
                estado=EstadoAlerta.ACTIVA,
                mensaje=f"{nombre}: stock actual {st.cantidad}, mínimo {st.stock_minimo}",
            )
            creadas.append(self._alertas.crear(alerta))
        return creadas
