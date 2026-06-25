"""Puerto: Repositorio de Productos."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.producto import Producto


class RepositorioProducto(ABC):
    @abstractmethod
    def obtener_por_id(self, producto_id: int) -> Optional[Producto]: ...

    @abstractmethod
    def obtener_por_sku(self, sku: str) -> Optional[Producto]: ...

    @abstractmethod
    def obtener_por_codigo_barra(self, codigo: str) -> Optional[Producto]: ...

    @abstractmethod
    def buscar(
        self, termino: str = "", categoria_id: Optional[int] = None, limit: int = 50
    ) -> List[Producto]: ...

    @abstractmethod
    def listar(self, solo_activos: bool = True) -> List[Producto]: ...

    @abstractmethod
    def crear(self, producto: Producto) -> Producto: ...

    @abstractmethod
    def actualizar(self, producto: Producto) -> Producto: ...

    @abstractmethod
    def eliminar(self, producto_id: int) -> None: ...
