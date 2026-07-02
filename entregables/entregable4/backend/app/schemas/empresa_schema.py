from decimal import Decimal

from pydantic import BaseModel, Field


class EmpresaResponse(BaseModel):
    idEmpresa: int
    nombreEmpresa: str
    isInicializado: bool
    timer_revision_minutos: int
    igv_porcentaje: Decimal
    moneda: str


class EmpresaUpdateRequest(BaseModel):
    nombreEmpresa: str | None = Field(default=None, min_length=2, max_length=150)
    timer_revision_minutos: int | None = Field(default=None, ge=1, le=1440)
    igv_porcentaje: Decimal | None = Field(default=None, ge=0, le=100)
    moneda: str | None = Field(default=None, min_length=3, max_length=3)
