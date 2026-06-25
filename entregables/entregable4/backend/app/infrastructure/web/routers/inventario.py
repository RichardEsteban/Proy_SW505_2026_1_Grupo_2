"""Router: inventario por sucursal."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.domain.use_cases.inventario.consultar_disponibilidad import (
    ConsultarDisponibilidad,
)
from app.domain.use_cases.inventario.verificar_stock_minimo import (
    VerificarStockMinimo,
)
from app.infrastructure.web.dependencies import (
    get_current_user,
    use_case_consultar_disponibilidad,
    use_case_verificar_stock_minimo,
)

router = APIRouter(prefix="/inventario", tags=["Inventario"])


@router.get("/disponibilidad")
def disponibilidad(
    sucursal_id: int = Query(...),
    termino: str = "",
    solo_bajo_minimo: bool = False,
    uc: ConsultarDisponibilidad = Depends(use_case_consultar_disponibilidad),
    user: dict = Depends(get_current_user),
) -> list:
    return [item.__dict__ for item in uc.ejecutar(sucursal_id, termino, solo_bajo_minimo)]


@router.post("/verificar-stock-minimo")
def verificar_stock(
    sucursal_id: int = Query(...),
    uc: VerificarStockMinimo = Depends(use_case_verificar_stock_minimo),
    user: dict = Depends(get_current_user),
) -> dict:
    alertas = uc.ejecutar(sucursal_id)
    return {"alertas_creadas": len(alertas), "alertas": [a.__dict__ for a in alertas]}
