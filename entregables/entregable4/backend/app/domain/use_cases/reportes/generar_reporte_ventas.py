"""Caso de uso: Generar reporte de ventas."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from app.application.ports.generador_reporte import GeneradorReporte


class GenerarReporteVentas:
    def __init__(self, generador: GeneradorReporte) -> None:
        self._gen = generador

    def ejecutar(
        self,
        fecha_desde: datetime,
        fecha_hasta: datetime,
        sucursal_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        return self._gen.ventas(fecha_desde, fecha_hasta, sucursal_id)
