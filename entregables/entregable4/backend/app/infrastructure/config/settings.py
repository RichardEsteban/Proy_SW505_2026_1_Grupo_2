"""Configuración central hardcoded (sin .env).

Para producción real, sobreescribir mediante variables de entorno del sistema
o variables de Docker en docker-compose.yml.
"""
from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Todas las configuraciones tienen valores por defecto hardcoded."""

    # Ya NO lee de .env: solo defaults del código + env del sistema / Docker
    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore",
    )

    # ==================== APP ====================
    app_name: str = "sistema-inventario"
    app_env: str = "development"
    app_debug: bool = True
    app_port: int = 8000
    # CSV con los orígenes permitidos para CORS
    app_cors_origins: str = "http://localhost,http://localhost:80,http://localhost:5173"

    # ==================== DATABASE (MySQL) ====================
    database_url: str = "mysql+pymysql://inventario:inventario@db:3306/inventario"
    db_host: str = "db"
    db_port: int = 3306
    db_name: str = "inventario"
    db_user: str = "inventario"
    db_password: str = "inventario"
    db_root_password: str = "rootpass"

    # ==================== JWT ====================
    jwt_secret: str = "jwt-secret-fijo-desarrollo-cambiar-en-produccion-2026"
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 480

    # ==================== MINIO ====================
    minio_endpoint: str = "minio:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "comprobantes"
    minio_secure: bool = False

    # ==================== SMTP ====================
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "no-reply@sistema-inventario.local"

    # ==================== IGV ====================
    igv_porcentaje: float = 18.0
    moneda: str = "PEN"

    # ==================== WIZARD ====================
    wizard_admin_dni: str = "00000000"
    wizard_admin_nombre: str = "Administrador"
    wizard_admin_password: str = "Admin123*"

    # ==================== HELPERS ====================
    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.app_cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """Singleton de settings cacheado."""
    return Settings()