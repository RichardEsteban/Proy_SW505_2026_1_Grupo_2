from pydantic import BaseModel, EmailStr, Field


class ProveedorCreateRequest(BaseModel):
    identificacionFiscal: str = Field(min_length=8, max_length=11)
    razonSocial: str = Field(min_length=2, max_length=150)
    contactoNombre: str | None = Field(default=None, max_length=100)
    telefono: str | None = Field(default=None, max_length=20)
    correoElectronico: EmailStr | None = None
    direccion: str | None = Field(default=None, max_length=255)


class ProveedorUpdateRequest(BaseModel):
    identificacionFiscal: str | None = Field(default=None, min_length=8, max_length=11)
    razonSocial: str | None = Field(default=None, min_length=2, max_length=150)
    contactoNombre: str | None = Field(default=None, max_length=100)
    telefono: str | None = Field(default=None, max_length=20)
    correoElectronico: EmailStr | None = None
    direccion: str | None = Field(default=None, max_length=255)
    isActivo: bool | None = None


class ProveedorResponse(BaseModel):
    idProveedor: int
    idEmpresa: int
    identificacionFiscal: str
    razonSocial: str
    contactoNombre: str | None
    telefono: str | None
    correoElectronico: str | None
    direccion: str | None
    isActivo: bool
