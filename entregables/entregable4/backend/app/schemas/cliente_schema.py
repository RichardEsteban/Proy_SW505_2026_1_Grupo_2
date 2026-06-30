from pydantic import BaseModel, EmailStr
from typing import Optional


class ClientePersona(BaseModel):
    documentoIdentidad: str
    nombres: str
    apellidos: str


class ClienteEmpresa(BaseModel):
    identificacionFiscal: str
    razonSocial: str
    direccionFiscal: Optional[str] = None


class ClienteCreate(BaseModel):
    tipoCliente: str  # PERSONA | EMPRESA
    telefono: Optional[str] = None
    correoElectronico: Optional[EmailStr] = None

    persona: Optional[ClientePersona] = None
    empresa: Optional[ClienteEmpresa] = None


class ClienteResponse(BaseModel):
    idCliente: int
    tipoCliente: str
    telefono: Optional[str]
    correoElectronico: Optional[EmailStr]

    persona: Optional[ClientePersona] = None
    empresa: Optional[ClienteEmpresa] = None

    class Config:
        from_attributes = True