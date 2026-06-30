from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

from app.core.config import get_settings


settings = get_settings()


def crear_access_token(data: dict[str, Any]) -> str:
    datos = data.copy()

    expiracion = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    datos.update({"exp": expiracion})

    token = jwt.encode(
        datos,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )

    return token


def decodificar_token(token: str) -> dict[str, Any] | None:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError:
        return None