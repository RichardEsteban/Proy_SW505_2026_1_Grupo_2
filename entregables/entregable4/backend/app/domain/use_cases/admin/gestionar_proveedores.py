"""Caso de uso: Gestión de proveedores."""
from __future__ import annotations

from typing import List, Optional

from app.domain.entities.proveedor import Proveedor


class GestionarProveedores:
    def __init__(self, repo) -> None:
        self._repo = repo

    def listar(self, solo_activos: bool = True) -> List[Proveedor]:
        return self._repo.listar(solo_activos=solo_activos)

    def obtener(self, proveedor_id: int) -> Optional[Proveedor]:
        return self._repo.obtener_por_id(proveedor_id)

    def crear(
        self,
        ruc: str,
        razon_social: str,
        nombre_comercial: Optional[str] = None,
        direccion: Optional[str] = None,
        telefono: Optional[str] = None,
        email: Optional[str] = None,
        contacto_nombre: Optional[str] = None,
        contacto_telefono: Optional[str] = None,
    ) -> Proveedor:
        if self._repo.obtener_por_ruc(ruc):
            raise ValueError(f"RUC {ruc} ya registrado")
        prov = Proveedor(
            id=None,
            ruc=ruc,
            razon_social=razon_social,
            nombre_comercial=nombre_comercial,
            direccion=direccion,
            telefono=telefono,
            email=email,
            contacto_nombre=contacto_nombre,
            contacto_telefono=contacto_telefono,
        )
        return self._repo.crear(prov)

    def actualizar(self, proveedor: Proveedor) -> Proveedor:
        return self._repo.actualizar(proveedor)
