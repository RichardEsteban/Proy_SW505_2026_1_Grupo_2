"""Router: ventas (POS)."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.domain.entities.venta import TipoComprobante
from app.domain.exceptions.stock_insuficiente import StockInsuficienteError
from app.domain.use_cases.ventas.calcular_totales import (
    CalcularTotales,
    ItemCalculo,
)
from app.domain.use_cases.ventas.generar_comprobante import GenerarComprobante
from app.domain.use_cases.ventas.registrar_venta import (
    ItemVentaInput,
    RegistrarVenta,
    VentaInput,
)
from app.infrastructure.web.dependencies import (
    get_current_user,
    get_repo_ventas,
    use_case_calcular_totales,
    use_case_generar_comprobante,
    use_case_registrar_venta,
)

router = APIRouter(prefix="/ventas", tags=["Ventas"])


# --- Schemas ---
class ItemVentaSchema(BaseModel):
    producto_id: int
    cantidad: float = Field(gt=0)
    precio_unitario: float = Field(gt=0)
    descuento: float = 0


class RegistrarVentaIn(BaseModel):
    serie: str
    numero: str
    tipo_comprobante: TipoComprobante
    sucursal_id: int
    cliente_id: Optional[int] = None
    items: List[ItemVentaSchema]


class CalculoIn(BaseModel):
    items: List[ItemCalculo]


# --- Endpoints ---
@router.post("/calcular")
def calcular(
    datos: CalculoIn,
    uc: CalcularTotales = Depends(use_case_calcular_totales),
) -> dict:
    return uc.ejecutar(datos.items).__dict__


@router.post("", status_code=201)
def registrar_venta(
    datos: RegistrarVentaIn,
    uc: RegistrarVenta = Depends(use_case_registrar_venta),
    user: dict = Depends(get_current_user),
) -> dict:
    try:
        venta = uc.ejecutar(
            VentaInput(
                serie=datos.serie,
                numero=datos.numero,
                tipo_comprobante=datos.tipo_comprobante,
                sucursal_id=datos.sucursal_id,
                usuario_id=int(user["sub"]),
                cliente_id=datos.cliente_id,
                items=[ItemVentaInput(**i.model_dump()) for i in datos.items],
            )
        )
    except StockInsuficienteError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {
        "id": venta.id,
        "serie": venta.serie,
        "numero": venta.numero,
        "total": venta.total,
        "subtotal": venta.subtotal,
        "igv": venta.igv,
        "estado": venta.estado.value,
    }


@router.get("")
def listar_ventas(
    sucursal_id: Optional[int] = None,
    fecha_desde: Optional[datetime] = None,
    fecha_hasta: Optional[datetime] = None,
    limit: int = Query(50, le=200),
    repo=Depends(get_repo_ventas),
    user: dict = Depends(get_current_user),
) -> list:
    return [
        {
            "id": v.id,
            "serie": v.serie,
            "numero": v.numero,
            "tipo_comprobante": v.tipo_comprobante.value,
            "total": v.total,
            "estado": v.estado.value,
            "fecha": v.fecha.isoformat(),
        }
        for v in repo.listar(sucursal_id, fecha_desde, fecha_hasta, limit)
    ]


@router.post("/{venta_id}/comprobante")
def generar_comprobante(
    venta_id: int,
    uc: GenerarComprobante = Depends(use_case_generar_comprobante),
    user: dict = Depends(get_current_user),
) -> dict:
    try:
        url = uc.ejecutar(venta_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"pdf_url": url}
