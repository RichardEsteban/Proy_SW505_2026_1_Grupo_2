"""Servicios compartidos de infraestructura: JWT, password hashing."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.infrastructure.config.settings import get_settings


_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
_settings = get_settings()


class JWTService:
    """Emite y verifica tokens JWT."""

    def __init__(self) -> None:
        self.secret = _settings.jwt_secret
        self.algorithm = _settings.jwt_algorithm
        self.default_expire = _settings.jwt_expires_minutes

    def emitir_token(
        self,
        payload: Dict[str, Any],
        expira_en_minutos: Optional[int] = None,
    ) -> str:
        minutos = expira_en_minutos or self.default_expire
        to_encode = payload.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=minutos)
        to_encode["exp"] = expire
        return jwt.encode(to_encode, self.secret, algorithm=self.algorithm)

    def verificar_token(self, token: str) -> Dict[str, Any]:
        try:
            return jwt.decode(token, self.secret, algorithms=[self.algorithm])
        except JWTError as e:
            raise ValueError(f"Token inválido: {e}") from e

    @staticmethod
    def hash_password(password: str) -> str:
        return _pwd_context.hash(password)

    @staticmethod
    def verificar_password(password_plano: str, password_hash: str) -> bool:
        return _pwd_context.verify(password_plano, password_hash)


# Singleton
jwt_service = JWTService()
