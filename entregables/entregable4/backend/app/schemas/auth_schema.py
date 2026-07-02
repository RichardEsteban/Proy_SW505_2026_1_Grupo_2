from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    correoElectronico: EmailStr
    contrasena: str
    forzarCierreSesion: bool = False


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


class RecuperarContrasenaRequest(BaseModel):
    correoElectronico: EmailStr


class VerificarCodigoRequest(BaseModel):
    correoElectronico: EmailStr
    codigo: str = Field(..., min_length=6, max_length=6)


class CambiarContrasenaRequest(BaseModel):
    correoElectronico: EmailStr
    codigo: str = Field(..., min_length=6, max_length=6)
    nuevaContrasena: str = Field(..., min_length=8)
    confirmarContrasena: str = Field(..., min_length=8)


class MensajeResponse(BaseModel):
    mensaje: str
