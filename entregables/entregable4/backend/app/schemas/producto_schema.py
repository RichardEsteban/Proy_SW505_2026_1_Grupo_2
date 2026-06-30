from pydantic import BaseModel


class ProductoCreate(BaseModel):
    idEmpresa: int
    codigoBarras: str
    nombreProducto: str
    precioVenta: float


class ProductoResponse(BaseModel):
    idProducto: int
    idEmpresa: int
    codigoBarras: str
    nombreProducto: str
    precioVenta: float
    porcentajeIgv: float
    isActivo: bool

    class Config:
        from_attributes = True