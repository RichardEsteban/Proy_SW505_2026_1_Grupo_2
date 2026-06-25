"""Caso de uso: Cambiar contraseña (con o sin forzar)."""
from __future__ import annotations

from app.application.ports.repositorio_usuario import RepositorioUsuario
from app.domain.exceptions.credenciales_invalidas import CredencialesInvalidasError


class CambiarPassword:
    def __init__(self, repo_usuarios: RepositorioUsuario, jwt_service) -> None:
        self._repo = repo_usuarios
        self._jwt = jwt_service

    def ejecutar(
        self, usuario_id: int, password_actual: str, password_nueva: str
    ) -> None:
        usuario = self._repo.obtener_por_id(usuario_id)
        if usuario is None:
            raise CredencialesInvalidasError("Usuario no encontrado")

        if not self._jwt.verificar_password(password_actual, usuario.password_hash):
            raise CredencialesInvalidasError("La contraseña actual no es correcta")

        if len(password_nueva) < 8:
            raise ValueError("La nueva contraseña debe tener al menos 8 caracteres")

        usuario.password_hash = self._jwt.hash_password(password_nueva)
        usuario.debe_cambiar_password = False
        self._repo.actualizar(usuario)
