"""Router: autenticación y cuentas."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from app.domain.exceptions.credenciales_invalidas import CredencialesInvalidasError
from app.domain.use_cases.accesos.autenticar_usuario import AutenticarUsuario
from app.domain.use_cases.accesos.cambiar_password import CambiarPassword
from app.domain.use_cases.accesos.inicializar_sistema import InicializarSistema
from app.domain.use_cases.accesos.recuperar_password import RecuperarPassword
from app.infrastructure.web.dependencies import (
    get_current_user,
    use_case_autenticar,
    use_case_cambiar_password,
    use_case_inicializar,
    use_case_recuperar_password,
)

router = APIRouter(prefix="/auth", tags=["Autenticación"])


# --- Schemas ---
class LoginIn(BaseModel):
    username: str
    password: str


class LoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario_id: int
    username: str
    nombre_completo: str
    rol: str
    sucursal_id: int | None
    debe_cambiar_password: bool


class CambiarPasswordIn(BaseModel):
    password_actual: str
    password_nueva: str = Field(min_length=8)


class RecuperarIn(BaseModel):
    email: EmailStr


class RestablecerIn(BaseModel):
    token: str
    password_nueva: str = Field(min_length=8)


class WizardIn(BaseModel):
    admin_dni: str
    admin_nombre: str
    admin_apellido: str
    admin_email: EmailStr
    admin_username: str
    admin_password: str = Field(min_length=8)
    empresa_nombre: str
    empresa_ruc: str
    igv_porcentaje: float = 18.0
    moneda: str = "PEN"
    sucursal_nombre: str = "Sucursal Principal"
    almacen_nombre: str = "Almacén Central"


# --- Endpoints ---
@router.post("/login", response_model=LoginOut)
def login(
    datos: LoginIn,
    uc: AutenticarUsuario = Depends(use_case_autenticar),
) -> LoginOut:
    try:
        r = uc.ejecutar(datos.username, datos.password)
    except CredencialesInvalidasError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    return LoginOut(
        access_token=r.access_token,
        usuario_id=r.usuario_id,
        username=r.username,
        nombre_completo=r.nombre_completo,
        rol=r.rol,
        sucursal_id=r.sucursal_id,
        debe_cambiar_password=r.debe_cambiar_password,
    )


@router.post("/cambiar-password")
def cambiar_password(
    datos: CambiarPasswordIn,
    uc: CambiarPassword = Depends(use_case_cambiar_password),
    user: dict = Depends(get_current_user),
) -> dict:
    try:
        uc.ejecutar(int(user["sub"]), datos.password_actual, datos.password_nueva)
    except CredencialesInvalidasError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True, "mensaje": "Contraseña actualizada"}


@router.post("/recuperar-password")
def recuperar_password(
    datos: RecuperarIn,
    uc: RecuperarPassword = Depends(use_case_recuperar_password),
) -> dict:
    uc.solicitar(datos.email)
    return {"ok": True, "mensaje": "Si el email existe, se enviará un token."}


@router.post("/restablecer-password")
def restablecer(
    datos: RestablecerIn,
    uc: RecuperarPassword = Depends(use_case_recuperar_password),
) -> dict:
    try:
        uc.restablecer(datos.token, datos.password_nueva)
    except CredencialesInvalidasError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True, "mensaje": "Contraseña restablecida"}


@router.post("/wizard-inicial")
def wizard_inicial(
    datos: WizardIn,
    uc: InicializarSistema = Depends(use_case_inicializar),
) -> dict:
    from app.domain.use_cases.accesos.inicializar_sistema import DatosInicializacion

    return uc.ejecutar(
        DatosInicializacion(
            admin_dni=datos.admin_dni,
            admin_nombre=datos.admin_nombre,
            admin_apellido=datos.admin_apellido,
            admin_email=datos.admin_email,
            admin_username=datos.admin_username,
            admin_password=datos.admin_password,
            empresa_nombre=datos.empresa_nombre,
            empresa_ruc=datos.empresa_ruc,
            igv_porcentaje=datos.igv_porcentaje,
            moneda=datos.moneda,
            sucursal_nombre=datos.sucursal_nombre,
            almacen_nombre=datos.almacen_nombre,
        )
    )


@router.get("/me")
def me(user: dict = Depends(get_current_user)) -> dict:
    return user
