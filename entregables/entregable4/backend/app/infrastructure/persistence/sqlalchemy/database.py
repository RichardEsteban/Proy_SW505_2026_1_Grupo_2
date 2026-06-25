"""Configuración de SQLAlchemy: engine, SessionLocal, Base, dependency."""
from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.infrastructure.config.settings import get_settings


class Base(DeclarativeBase):
    """Base declarativa para todos los modelos ORM."""
    pass


_settings = get_settings()

# Detectar si es MySQL para añadir charset
_connect_args = {}
if _settings.database_url.startswith("mysql"):
    _connect_args = {"charset": "utf8mb4"}

engine = create_engine(
    _settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=False,
    future=True,
    connect_args=_connect_args,
)

SessionLocal = sessionmaker(
    bind=engine, autocommit=False, autoflush=False, expire_on_commit=False
)


def get_db() -> Generator[Session, None, None]:
    """Dependencia FastAPI para inyectar una sesión por request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Context manager para uso fuera de FastAPI (scripts, tests, etc.)."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
