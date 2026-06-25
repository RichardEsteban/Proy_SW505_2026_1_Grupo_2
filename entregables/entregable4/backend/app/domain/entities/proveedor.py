"""Entidades: Proveedor y Cliente."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Proveedor:
    id: Optional[int]
    ruc: str
    razon_social: str
    nombre_comercial: Optional[str]
    direccion: Optional[str]
    telefono: Optional[str]
    email: Optional[str]
    contacto_nombre: Optional[str] = None
    contacto_telefono: Optional[str] = None
    activo: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class Cliente:
    id: Optional[int]
    tipo_documento: str  # "DNI" | "RUC"
    numero_documento: str
    nombre: str
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    activo: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
