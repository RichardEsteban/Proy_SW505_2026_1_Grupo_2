from datetime import datetime
from typing import Literal

from pydantic import BaseModel


EstadoAlerta = Literal["PENDIENTE", "LEIDA"]
TipoAlerta = Literal["STOCK_MINIMO", "STOCK_AGOTADO"]


class AlertaStockResponse(BaseModel):
    idAlerta: int
    idUbicacion: int
    ubicacion: str
    idProducto: int
    producto: str
    tipoAlerta: TipoAlerta
    cantidadActual: int
    stockReferencia: int
    estado: EstadoAlerta
    fechaCreacion: datetime
    fechaLeida: datetime | None
