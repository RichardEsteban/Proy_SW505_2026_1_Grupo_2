"""Punto de entrada FastAPI: instancia la app, monta routers, CORS y healthcheck."""
from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.infrastructure.config.settings import get_settings
from app.infrastructure.web.routers import (
    admin,
    almacen,
    auth,
    inventario,
    reportes,
    reposicion,
    ventas,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="API REST para sistema de inventario y ventas (POS).",
    debug=settings.app_debug,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Meta"])
def health() -> JSONResponse:
    return JSONResponse({"status": "ok", "app": settings.app_name, "env": settings.app_env})


# Routers
app.include_router(auth.router, prefix="/api")
app.include_router(ventas.router, prefix="/api")
app.include_router(inventario.router, prefix="/api")
app.include_router(reposicion.router, prefix="/api")
app.include_router(almacen.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(reportes.router, prefix="/api")


@app.get("/", tags=["Meta"])
def root() -> dict:
    return {
        "app": settings.app_name,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }
