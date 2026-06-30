from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UsuarioBase(BaseModel):
    correoElectronico: EmailStr


class UsuarioCreate(UsuarioBase):
    contrasena: str
    idRol: int
    idUbicacion: int


class UsuarioUpdate(BaseModel):
    correoElectronico: Optional[EmailStr] = None
    idRol: Optional[int] = None
    idUbicacion: Optional[int] = None
    isActivo: Optional[bool] = None


class UsuarioResponse(BaseModel):
    idUsuario: int
    correoElectronico: EmailStr
    idRol: int
    idUbicacion: int
    isActivo: bool
    isContrasenaTemporal: bool
    fechaCreacion: datetime

    class Config:
        from_attributes = True