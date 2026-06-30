from pydantic import BaseModel, EmailStr
from typing import Optional


class ProveedorCreate(BaseModel):
    idEmpresa: int
    identificacionFiscal: str
    razonSocial: str


class ProveedorResponse(BaseModel):
    idProveedor: int
    idEmpresa: int
    identificacionFiscal: str
    razonSocial: str
    contactoNombre: Optional[str]
    telefono: Optional[str]
    correoElectronico: Optional[EmailStr]
    direccion: Optional[str]
    isActivo: bool

    class Config:
        from_attributes = True