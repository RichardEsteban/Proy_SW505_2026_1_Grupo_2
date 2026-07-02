from typing import Literal

from pydantic import BaseModel, Field


TipoUbicacion = Literal["ALMACEN", "SUCURSAL"]


class UbicacionCreateRequest(BaseModel):
    nombreUbicacion: str = Field(min_length=2, max_length=150)
    tipoUbicacion: TipoUbicacion
    direccion: str = Field(min_length=2, max_length=255)


class UbicacionUpdateRequest(BaseModel):
    nombreUbicacion: str | None = Field(default=None, min_length=2, max_length=150)
    tipoUbicacion: TipoUbicacion | None = None
    direccion: str | None = Field(default=None, min_length=2, max_length=255)
    isActivo: bool | None = None


class UbicacionResponse(BaseModel):
    idUbicacion: int
    idEmpresa: int
    nombreUbicacion: str
    tipoUbicacion: str
    direccion: str
    isActivo: bool
