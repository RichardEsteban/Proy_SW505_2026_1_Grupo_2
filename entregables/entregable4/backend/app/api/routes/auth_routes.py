from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencias import get_current_user
from app.db.session import get_db
from app.schemas.auth_schema import LoginRequest, TokenResponse, UsuarioAuthResponse
from app.services.auth_service import AuthService


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