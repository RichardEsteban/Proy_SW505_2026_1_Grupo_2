"""Puerto: Repositorio de Usuarios (interfaz abstracta)."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.usuario import Usuario


class RepositorioUsuario(ABC):
    @abstractmethod
    def obtener_por_id(self, usuario_id: int) -> Optional[Usuario]: ...

    @abstractmethod
    def obtener_por_username(self, username: str) -> Optional[Usuario]: ...

    @abstractmethod
    def obtener_por_dni(self, dni: str) -> Optional[Usuario]: ...

    @abstractmethod
    def listar(self, sucursal_id: Optional[int] = None) -> List[Usuario]: ...

    @abstractmethod
    def crear(self, usuario: Usuario) -> Usuario: ...

    @abstractmethod
    def actualizar(self, usuario: Usuario) -> Usuario: ...

    @abstractmethod
    def eliminar(self, usuario_id: int) -> None: ...
