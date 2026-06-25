"""Caso de uso: Recuperar contraseña (genera token + envía email)."""
from __future__ import annotations

from dataclasses import dataclass

from app.application.ports.repositorio_usuario import RepositorioUsuario
from app.domain.exceptions.credenciales_invalidas import CredencialesInvalidasError


@dataclass
class TokenRecuperacion:
    email: str
    token: str
    expira_en_minutos: int = 30


class RecuperarPassword:
    def __init__(
        self,
        repo_usuarios: RepositorioUsuario,
        email_service,
        jwt_service,
    ) -> None:
        self._repo = repo_usuarios
        self._email = email_service
        self._jwt = jwt_service

    def solicitar(self, email: str) -> TokenRecuperacion:
        # No revelar si el email existe
        usuario = next(
            (u for u in self._repo.listar() if u.email.lower() == email.lower()),
            None,
        )
        if usuario is None:
            # Devolvemos token "vacío" para no filtrar existencia
            return TokenRecuperacion(email=email, token="")

        token = self._jwt.emitir_token(
            {"sub": str(usuario.id), "scope": "reset"},
            expira_en_minutos=30,
        )
        try:
            self._email.enviar(
                destinatario=email,
                asunto="Recuperación de contraseña",
                cuerpo_html=f"<p>Hola {usuario.nombre},</p>"
                f"<p>Usa este token para restablecer tu contraseña:</p>"
                f"<p><b>{token}</b></p>"
                f"<p>Caduca en 30 minutos.</p>",
            )
        except Exception:
            # En dev no debe romper el flujo
            pass
        return TokenRecuperacion(email=email, token=token)

    def restablecer(self, token: str, password_nueva: str) -> None:
        payload = self._jwt.verificar_token(token)
        if payload.get("scope") != "reset":
            raise CredencialesInvalidasError("Token inválido")

        usuario_id = int(payload["sub"])
        usuario = self._repo.obtener_por_id(usuario_id)
        if usuario is None:
            raise CredencialesInvalidasError("Usuario no encontrado")

        usuario.password_hash = self._jwt.hash_password(password_nueva)
        usuario.debe_cambiar_password = False
        self._repo.actualizar(usuario)
