"""Caso de uso: Gestión de clientes."""
from __future__ import annotations

from typing import List, Optional

from app.domain.entities.proveedor import Cliente


class GestionarClientes:
    def __init__(self, repo) -> None:
        self._repo = repo

    def listar(self, termino: str = "", limit: int = 100) -> List[Cliente]:
        return self._repo.buscar(termino=termino, limit=limit)

    def obtener(self, cliente_id: int) -> Optional[Cliente]:
        return self._repo.obtener_por_id(cliente_id)

    def crear(
        self,
        tipo_documento: str,
        numero_documento: str,
        nombre: str,
        direccion: Optional[str] = None,
        telefono: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Cliente:
        if self._repo.obtener_por_documento(tipo_documento, numero_documento):
            raise ValueError("Cliente ya registrado con ese documento")
        cli = Cliente(
            id=None,
            tipo_documento=tipo_documento,
            numero_documento=numero_documento,
            nombre=nombre,
            direccion=direccion,
            telefono=telefono,
            email=email,
        )
        return self._repo.crear(cli)

    def actualizar(self, cliente: Cliente) -> Cliente:
        return self._repo.actualizar(cliente)
