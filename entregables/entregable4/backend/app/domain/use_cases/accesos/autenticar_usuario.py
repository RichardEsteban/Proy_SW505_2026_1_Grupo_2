"""Caso de uso: Autenticar usuario (login)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.application.ports.repositorio_usuario import RepositorioUsuario
from app.domain.entities.usuario import EstadoUsuario
from app.domain.exceptions.credenciales_invalidas import CredencialesInvalidasError


@dataclass
class ResultadoAuth:
    usuario_id: int
    username: str
    nombre_completo: str
    rol: str
    sucursal_id: Optional[int]
    debe_cambiar_password: bool
    access_token: str
    refresh_token: Optional[str] = None


class AutenticarUsuario:
    """Verifica credenciales y emite un JWT."""

    MAX_INTENTOS = 5

    def __init__(self, repo_usuarios: RepositorioUsuario, jwt_service) -> None:
        self._repo = repo_usuarios
        self._jwt = jwt_service

    def ejecutar(
        self, username: str, password: str
    ) -> ResultadoAuth:
        usuario = self._repo.obtener_por_username(username)
        if usuario is None:
            raise CredencialesInvalidasError("Usuario o contraseña incorrectos")

        if usuario.estado == EstadoUsuario.BLOQUEADO:
            raise CredencialesInvalidasError("Cuenta bloqueada. Contacte al admin.")
        if usuario.estado == EstadoUsuario.INACTIVO:
            raise CredencialesInvalidasError("Cuenta inactiva.")

        # El hash se valida fuera (Passlib lo inyecta el servicio web)
        if not self._jwt.verificar_password(password, usuario.password_hash):
            usuario.registrar_intento_fallido(self.MAX_INTENTOS)
            self._repo.actualizar(usuario)
            raise CredencialesInvalidasError("Usuario o contraseña incorrectos")

        # Reset intentos + último acceso
        usuario.intentos_fallidos = 0
        usuario.ultimo_acceso = datetime.utcnow()
        self._repo.actualizar(usuario)

        token = self._jwt.emitir_token(
            {
                "sub": str(usuario.id),
                "username": usuario.username,
                "rol": str(usuario.rol_id),
                "sucursal": usuario.sucursal_id,
            }
        )
        return ResultadoAuth(
            usuario_id=usuario.id,
            username=usuario.username,
            nombre_completo=usuario.nombre_completo,
            rol=str(usuario.rol_id),
            sucursal_id=usuario.sucursal_id,
            debe_cambiar_password=usuario.debe_cambiar_password,
            access_token=token,
        )
