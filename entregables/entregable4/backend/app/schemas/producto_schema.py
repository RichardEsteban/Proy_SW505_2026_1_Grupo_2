from decimal import Decimal

from pydantic import BaseModel, Field


class ProductoCreateRequest(BaseModel):
    codigoBarras: str = Field(min_length=1, max_length=50)
    nombreProducto: str = Field(min_length=2, max_length=150)
    idCategoria: int | None = None
    precioVenta: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    porcentajeIgv: Decimal = Field(default=Decimal("18.00"), ge=0, le=100, max_digits=5, decimal_places=2)


class ProductoUpdateRequest(BaseModel):
    codigoBarras: str | None = Field(default=None, min_length=1, max_length=50)
    nombreProducto: str | None = Field(default=None, min_length=2, max_length=150)
    idCategoria: int | None = None
    precioVenta: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    porcentajeIgv: Decimal | None = Field(default=None, ge=0, le=100, max_digits=5, decimal_places=2)
    isActivo: bool | None = None


class ProductoResponse(BaseModel):
    idProducto: int
    idEmpresa: int
    idCategoria: int | None
    categoria: str | None
    codigoBarras: str
    nombreProducto: str
    precioVenta: Decimal
    porcentajeIgv: Decimal
    isActivo: bool
