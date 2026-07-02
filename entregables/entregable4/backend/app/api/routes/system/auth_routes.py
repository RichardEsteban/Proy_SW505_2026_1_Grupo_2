from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencias import get_current_user, oauth2_scheme
from app.db.session import get_db
from app.schemas.auth_schema import (
    CambiarContrasenaRequest,
    LoginRequest,
    MensajeResponse,
    RecuperarContrasenaRequest,
    TokenResponse,
    UsuarioAuthResponse,
    VerificarCodigoRequest,
)
from app.services.auth_service import AuthService
from app.utils.jwt import decodificar_token


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post("/login", response_model=TokenResponse)
def login(
    datos: LoginRequest,
    db: Session = Depends(get_db)
):
    return AuthService.login(db=db, datos=datos)


@router.get("/me", response_model=UsuarioAuthResponse)
def obtener_mi_usuario(
    usuario=Depends(get_current_user)
):
    return AuthService._crear_usuario_response(usuario)


@router.post("/logout", response_model=MensajeResponse)
def logout(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    payload = decodificar_token(token) or {}
    return AuthService.cerrar_sesion(db=db, token_id=payload.get("sid"))


@router.post("/forgot-password", response_model=MensajeResponse)
def solicitar_codigo_recuperacion(
    datos: RecuperarContrasenaRequest,
    db: Session = Depends(get_db)
):
    return AuthService.solicitar_codigo_recuperacion(db=db, datos=datos)


@router.post("/verify-reset-code", response_model=MensajeResponse)
def verificar_codigo_recuperacion(
    datos: VerificarCodigoRequest,
    db: Session = Depends(get_db)
):
    return AuthService.verificar_codigo_recuperacion(db=db, datos=datos)


@router.post("/reset-password", response_model=MensajeResponse)
def cambiar_contrasena_con_codigo(
    datos: CambiarContrasenaRequest,
    db: Session = Depends(get_db)
):
    return AuthService.cambiar_contrasena_con_codigo(db=db, datos=datos)
