"""Caso de uso: Gestión de sucursales y almacenes."""
from __future__ import annotations

from typing import List, Optional

from app.domain.entities.transferencia import Almacen, Sucursal


class GestionarSucursales:
    def __init__(self, repo_sucursales, repo_almacenes) -> None:
        self._suc = repo_sucursales
        self._alm = repo_almacenes

    # Sucursales
    def listar_sucursales(self) -> List[Sucursal]:
        return self._suc.listar()

    def crear_sucursal(self, codigo: str, nombre: str, direccion: Optional[str], telefono: Optional[str]) -> Sucursal:
        s = Sucursal(id=None, codigo=codigo, nombre=nombre, direccion=direccion, telefono=telefono)
        return self._suc.crear(s)

    def actualizar_sucursal(self, s: Sucursal) -> Sucursal:
        return self._suc.actualizar(s)

    # Almacenes
    def listar_almacenes(self) -> List[Almacen]:
        return self._alm.listar()

    def crear_almacen(self, codigo: str, nombre: str, direccion: Optional[str], responsable_id: Optional[int] = None) -> Almacen:
        a = Almacen(id=None, codigo=codigo, nombre=nombre, direccion=direccion, responsable_id=responsable_id)
        return self._alm.crear(a)

    def actualizar_almacen(self, a: Almacen) -> Almacen:
        return self._alm.actualizar(a)
