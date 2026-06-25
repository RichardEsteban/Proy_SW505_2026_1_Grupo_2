"""Puerto: Repositorio de Alertas."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.alerta import Alerta, EstadoAlerta, TipoAlerta


class RepositorioAlerta(ABC):
    @abstractmethod
    def crear(self, alerta: Alerta) -> Alerta: ...

    @abstractmethod
    def listar(
        self,
        tipo: Optional[TipoAlerta] = None,
        estado: Optional[EstadoAlerta] = None,
        ubicacion_id: Optional[int] = None,
    ) -> List[Alerta]: ...

    @abstractmethod
    def atender(self, alerta_id: int) -> Alerta: ...

    @abstractmethod
    def descartar(self, alerta_id: int) -> Alerta: ...
