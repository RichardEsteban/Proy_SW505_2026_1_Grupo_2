"""Puerto: Generador de Reportes."""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional


class GeneradorReporte(ABC):
    @abstractmethod
    def ventas(
        self,
        fecha_desde: datetime,
        fecha_hasta: datetime,
        sucursal_id: Optional[int] = None,
    ) -> Dict[str, Any]: ...

    @abstractmethod
    def inventario(
        self, sucursal_id: Optional[int] = None
    ) -> Dict[str, Any]: ...

    @abstractmethod
    def dashboard(self, sucursal_id: Optional[int] = None) -> Dict[str, Any]: ...
