from pydantic import BaseModel


class MetodoPagoResponse(BaseModel):
    idMetodoPago: int
    nombreMetodo: str
    isActivo: bool

    class Config:
        from_attributes = True