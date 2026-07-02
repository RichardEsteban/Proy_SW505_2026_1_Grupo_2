from pydantic import BaseModel, EmailStr, Field


class UsuarioCreateRequest(BaseModel):
    correoElectronico: EmailStr
    contrasenaTemporal: str = Field(min_length=8, max_length=72)
    idRol: int
    idUbicacion: int


class UsuarioUpdateRequest(BaseModel):
    correoElectronico: EmailStr | None = None
    idRol: int | None = None
    idUbicacion: int | None = None
    isActivo: bool | None = None


class CambiarContrasenaRequest(BaseModel):
    contrasenaActual: str = Field(min_length=1, max_length=72)
    contrasenaNueva: str = Field(min_length=8, max_length=72)


class UsuarioResponse(BaseModel):
    idUsuario: int
    correoElectronico: str
    idRol: int
    rol: str
    idUbicacion: int
    ubicacion: str
    tipoUbicacion: str
    isActivo: bool
    isContrasenaTemporal: bool
