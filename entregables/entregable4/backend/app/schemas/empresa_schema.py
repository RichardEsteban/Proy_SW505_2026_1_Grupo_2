from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class EmpresaResponse(BaseModel):
    idEmpresa: int
    nombreEmpresa: str
    isInicializado: bool
    fechaInicializacion: Optional[datetime]
    timer_revision_minutos: int
    igv_porcentaje: float
    moneda: str

    class Config:
        from_attributes = True