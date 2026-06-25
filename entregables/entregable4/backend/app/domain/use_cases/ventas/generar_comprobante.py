"""Caso de uso: Generar comprobante PDF de una venta."""
from __future__ import annotations

from app.application.ports.generador_pdf import GeneradorPDF
from app.application.ports.repositorio_venta import RepositorioVenta
from app.domain.exceptions.estado_invalido import EstadoInvalidoError


class GenerarComprobante:
    def __init__(
        self,
        repo_ventas: RepositorioVenta,
        generador_pdf: GeneradorPDF,
    ) -> None:
        self._ventas = repo_ventas
        self._pdf = generador_pdf

    def ejecutar(self, venta_id: int) -> str:
        venta = self._ventas.obtener_por_id(venta_id)
        if venta is None:
            raise EstadoInvalidoError(f"Venta {venta_id} no existe")
        if venta.estado.value == "ANULADA":
            raise EstadoInvalidoError("No se puede generar comprobante de venta anulada")

        contenido = self._pdf.generar_comprobante_venta(venta_id)
        nombre = f"comprobante_{venta.serie}-{venta.numero}.pdf"
        url = self._pdf.guardar(contenido, nombre)

        venta.pdf_url = url
        self._ventas.actualizar(venta) if hasattr(self._ventas, "actualizar") else None
        return url
