"""Punto de entrada de la aplicación.

Uso local:
    python run.py
o equivalente a:
    uvicorn app.infrastructure.web.main:app --reload
"""
from __future__ import annotations

import uvicorn

from app.infrastructure.config.settings import get_settings


def main() -> None:
    settings = get_settings()
    uvicorn.run(
        "app.infrastructure.web.main:app",
        host="0.0.0.0",
        port=settings.app_port,
        reload=settings.app_debug,
    )


if __name__ == "__main__":
    main()
