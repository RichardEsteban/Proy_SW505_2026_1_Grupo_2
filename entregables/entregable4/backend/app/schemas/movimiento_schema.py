from pydantic import BaseModel
from datetime import datetime


class MovimientoResponse(BaseModel):
    idMovimiento: int
    idUbicacion: int
    idProducto: int
    idUsuario: int
    cantidad: int
    tipoMovimiento: str
    motivoMovimiento: str
    tipoReferencia: str | None
    idReferencia: int | None
    fechaHora: datetime

    class Config:
        from_attributes = True