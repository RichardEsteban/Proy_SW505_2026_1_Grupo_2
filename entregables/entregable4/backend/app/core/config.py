from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Sistema MYPE POS"
    app_debug: bool = True

    database_url: str

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 480
    session_inactivity_minutes: int = 30
    session_heartbeat_grace_minutes: int = 2
    single_active_session: bool = True

    reset_code_expire_minutes: int = 3
    reset_code_resend_seconds: int = 60
    reset_code_max_attempts: int = 5

    smtp_enabled: bool = False
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = "codexventa@gmail.com"
    smtp_password: str = ""
    smtp_from_name: str = "Codex Venta"
    smtp_use_tls: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
