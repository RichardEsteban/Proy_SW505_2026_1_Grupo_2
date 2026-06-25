"""Caso de uso: Generar datos para dashboard (admin / sucursal)."""
from __future__ import annotations

from typing import Any, Dict, Optional

from app.application.ports.generador_reporte import GeneradorReporte


class GenerarDashboard:
    def __init__(self, generador: GeneradorReporte) -> None:
        self._gen = generador

    def ejecutar(self, sucursal_id: Optional[int] = None) -> Dict[str, Any]:
        return self._gen.dashboard(sucursal_id)
