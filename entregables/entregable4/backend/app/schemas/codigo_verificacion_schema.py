from pydantic import BaseModel
from datetime import datetime


class CodigoVerificacionCreate(BaseModel):
    idUsuario: int
    codigo: str
    fechaExpiracion: datetime


class CodigoVerificacionResponse(BaseModel):
    idCodigo: int
    idUsuario: int
    codigo: str
    isUsado: bool
    fechaExpiracion: datetime

    class Config:
        from_attributes = True