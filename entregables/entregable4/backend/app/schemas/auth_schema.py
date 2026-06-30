from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    correoElectronico: EmailStr
    contrasena: str


class UsuarioAuthResponse(BaseModel):
    idUsuario: int
    correoElectronico: str
    idRol: int
    rol: str
    idUbicacion: int
    ubicacion: str
    tipoUbicacion: str
    isContrasenaTemporal: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioAuthResponse