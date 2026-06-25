"""Caso de uso: Confirmar recepción de mercadería en sucursal."""
from __future__ import annotations

from app.application.ports.repositorio_solicitud import RepositorioSolicitud
from app.domain.entities.stock import TipoUbicacion
from app.domain.exceptions.estado_invalido import EstadoInvalidoError


class ConfirmarRecepcion:
    def __init__(self, repo_solicitudes: RepositorioSolicitud, repo_stock) -> None:
        self._solicitudes = repo_solicitudes
        self._stock = repo_stock

    def ejecutar(self, solicitud_id: int, recibido_por_id: int) -> None:
        sol = self._solicitudes.obtener_por_id(solicitud_id)
        if sol is None:
            raise EstadoInvalidoError(f"Solicitud {solicitud_id} no existe")
        if sol.estado.value not in ("APROBADA", "EN_TRANSITO"):
            raise EstadoInvalidoError(
                f"No se puede recibir una solicitud en estado {sol.estado.value}"
            )

        # Incrementar stock en sucursal destino
        for det in sol.detalles:
            stock = self._stock.obtener(
                producto_id=det.producto_id,
                ubicacion_tipo=TipoUbicacion.SUCURSAL,
                ubicacion_id=sol.sucursal_origen_id,
            )
            if stock is None:
                # Crear el registro si no existía
                from app.domain.entities.stock import Stock

                stock = Stock(
                    id=None,
                    producto_id=det.producto_id,
                    ubicacion_tipo=TipoUbicacion.SUCURSAL,
                    ubicacion_id=sol.sucursal_origen_id,
                    cantidad=0.0,
                    stock_minimo=0.0,
                )
                stock = self._stock.crear(stock)
            stock.incrementar(det.cantidad_recibida or det.cantidad_solicitada)
            self._stock.actualizar(stock)

        sol.recibir()
        self._solicitudes.actualizar(sol)
