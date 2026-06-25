"""Router: reportes y dashboard."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.domain.use_cases.reportes.generar_dashboard import GenerarDashboard
from app.domain.use_cases.reportes.generar_reporte_ventas import GenerarReporteVentas
from app.infrastructure.web.dependencies import (
    get_current_user,
    use_case_dashboard,
    use_case_reporte_ventas,
)

router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.get("/ventas")
def reporte_ventas(
    fecha_desde: datetime = Query(...),
    fecha_hasta: datetime = Query(...),
    sucursal_id: Optional[int] = None,
    uc: GenerarReporteVentas = Depends(use_case_reporte_ventas),
    _: dict = Depends(get_current_user),
) -> dict:
    return uc.ejecutar(fecha_desde, fecha_hasta, sucursal_id)


@router.get("/dashboard")
def dashboard(
    sucursal_id: Optional[int] = None,
    uc: GenerarDashboard = Depends(use_case_dashboard),
    _: dict = Depends(get_current_user),
) -> dict:
    return uc.ejecutar(sucursal_id)
