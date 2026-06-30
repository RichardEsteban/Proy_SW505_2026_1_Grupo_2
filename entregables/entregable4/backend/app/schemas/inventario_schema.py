from pydantic import BaseModel


class InventarioResponse(BaseModel):
    idInventario: int
    idUbicacion: int
    idProducto: int
    stockDisponible: int
    stockMinimo: int

    class Config:
        from_attributes = True