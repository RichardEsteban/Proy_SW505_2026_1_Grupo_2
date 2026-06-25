"""Entidad Sucursal, Almacén, Rol, MétodoPago y Transferencia."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


class EstadoTransferencia(str, Enum):
    INICIADA = "INICIADA"
    EN_TRANSITO = "EN_TRANSITO"
    RECIBIDA = "RECIBIDA"
    ANULADA = "ANULADA"


@dataclass
class Sucursal:
    id: Optional[int]
    codigo: str
    nombre: str
    direccion: Optional[str]
    telefono: Optional[str]
    activo: bool = True


@dataclass
class Almacen:
    id: Optional[int]
    codigo: str
    nombre: str
    direccion: Optional[str]
    responsable_id: Optional[int] = None
    activo: bool = True


@dataclass
class Rol:
    id: Optional[int]
    nombre: str
    descripcion: Optional[str] = None
    permisos: List[str] = field(default_factory=list)


@dataclass
class MetodoPago:
    id: Optional[int]
    nombre: str
    descripcion: Optional[str] = None
    activo: bool = True


@dataclass
class DetalleTransferencia:
    id: Optional[int]
    transferencia_id: Optional[int]
    producto_id: int
    cantidad: float


@dataclass
class Transferencia:
    id: Optional[int]
    codigo: str
    origen_tipo: str  # "SUCURSAL" | "ALMACEN"
    origen_id: int
    destino_tipo: str
    destino_id: int
    usuario_id: int
    estado: EstadoTransferencia = EstadoTransferencia.INICIADA
    fecha: Optional[datetime] = None
    detalles: List[DetalleTransferencia] = field(default_factory=list)
    observacion: Optional[str] = None
