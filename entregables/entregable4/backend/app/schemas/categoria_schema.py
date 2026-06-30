from pydantic import BaseModel
from typing import Optional


class CategoriaCreate(BaseModel):
    idEmpresa: int
    nombreCategoria: str
    descripcion: Optional[str] = None


class CategoriaResponse(BaseModel):
    idCategoria: int
    idEmpresa: int
    nombreCategoria: str
    descripcion: Optional[str]
    isActivo: bool

    class Config:
        from_attributes = True