"""Entidad Usuario - representa a un empleado del sistema."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class EstadoUsuario(str, Enum):
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"
    BLOQUEADO = "BLOQUEADO"


@dataclass
class Usuario:
    id: Optional[int]
    dni: str
    nombre: str
    apellido: str
    email: str
    username: str
    password_hash: str
    rol_id: int
    sucursal_id: Optional[int]
    estado: EstadoUsuario = EstadoUsuario.ACTIVO
    debe_cambiar_password: bool = True
    ultimo_acceso: Optional[datetime] = None
    intentos_fallidos: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    @property
    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellido}".strip()

    def bloquear(self) -> None:
        self.estado = EstadoUsuario.BLOQUEADO

    def activar(self) -> None:
        self.estado = EstadoUsuario.ACTIVO
        self.intentos_fallidos = 0

    def registrar_intento_fallido(self, max_intentos: int = 5) -> None:
        self.intentos_fallidos += 1
        if self.intentos_fallidos >= max_intentos:
            self.bloquear()
