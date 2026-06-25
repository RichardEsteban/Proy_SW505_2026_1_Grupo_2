"""Puerto: Repositorio de Ventas."""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from app.domain.entities.venta import Venta


class RepositorioVenta(ABC):
    @abstractmethod
    def crear(self, venta: Venta) -> Venta: ...

    @abstractmethod
    def obtener_por_id(self, venta_id: int) -> Optional[Venta]: ...

    @abstractmethod
    def listar(
        self,
        sucursal_id: Optional[int] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Venta]: ...

    @abstractmethod
    def anular(self, venta_id: int) -> Venta: ...

    @abstractmethod
    def siguiente_numero(self, serie: str) -> str: ...
