"""Router: almacén (entradas, compras, dashboard)."""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.domain.use_cases.almacen.registrar_compra import (
    ItemCompra,
    RegistrarCompra,
)
from app.domain.use_cases.almacen.registrar_entrada import (
    EntradaInput,
    ItemEntrada,
    RegistrarEntrada,
)
from app.infrastructure.web.dependencies import (
    get_current_user,
    use_case_registrar_compra,
    use_case_registrar_entrada,
)

router = APIRouter(prefix="/almacen", tags=["Almacén"])


class ItemEntradaSchema(BaseModel):
    producto_id: int
    cantidad: float
    stock_minimo: float = 0


class EntradaIn(BaseModel):
    almacen_id: int
    observacion: Optional[str] = None
    items: List[ItemEntradaSchema]


class ItemCompraSchema(BaseModel):
    producto_id: int
    cantidad: float
    precio_compra: float


class CompraIn(BaseModel):
    proveedor_id: int
    almacen_id: int
    numero_factura: str
    items: List[ItemCompraSchema]


@router.post("/entradas", status_code=201)
def registrar_entrada(
    datos: EntradaIn,
    uc: RegistrarEntrada = Depends(use_case_registrar_entrada),
    user: dict = Depends(get_current_user),
) -> dict:
    procesados = uc.ejecutar(
        EntradaInput(
            almacen_id=datos.almacen_id,
            observacion=datos.observacion,
            items=[ItemEntrada(**i.model_dump()) for i in datos.items],
        )
    )
    return {"items_procesados": procesados, "ok": True}


@router.post("/compras", status_code=201)
def registrar_compra(
    datos: CompraIn,
    uc: RegistrarCompra = Depends(use_case_registrar_compra),
    user: dict = Depends(get_current_user),
) -> dict:
    return uc.ejecutar(
        {
            "proveedor_id": datos.proveedor_id,
            "almacen_id": datos.almacen_id,
            "numero_factura": datos.numero_factura,
            "items": [ItemCompra(**i.model_dump()) for i in datos.items],
        }
    )
