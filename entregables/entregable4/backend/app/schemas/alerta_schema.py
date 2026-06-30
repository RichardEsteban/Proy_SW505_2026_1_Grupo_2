from pydantic import BaseModel
from datetime import datetime


class AlertaResponse(BaseModel):
    idAlerta: int
    idUbicacion: int
    idProducto: int
    tipoAlerta: str
    estado: str
    fechaCreacion: datetime

    class Config:
        from_attributes = True