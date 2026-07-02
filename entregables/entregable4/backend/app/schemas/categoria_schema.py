from pydantic import BaseModel, Field


class CategoriaCreateRequest(BaseModel):
    nombreCategoria: str = Field(min_length=2, max_length=100)
    descripcion: str | None = Field(default=None, max_length=200)


class CategoriaUpdateRequest(BaseModel):
    nombreCategoria: str | None = Field(default=None, min_length=2, max_length=100)
    descripcion: str | None = Field(default=None, max_length=200)
    isActivo: bool | None = None


class CategoriaResponse(BaseModel):
    idCategoria: int
    idEmpresa: int
    nombreCategoria: str
    descripcion: str | None
    isActivo: bool
