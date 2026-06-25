"""Puerto: Repositorio de Solicitudes de Reposición."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.solicitud import EstadoSolicitud, SolicitudReposicion


class RepositorioSolicitud(ABC):
    @abstractmethod
    def crear(self, solicitud: SolicitudReposicion) -> SolicitudReposicion: ...

    @abstractmethod
    def obtener_por_id(self, solicitud_id: int) -> Optional[SolicitudReposicion]: ...

    @abstractmethod
    def listar(
        self,
        sucursal_id: Optional[int] = None,
        estado: Optional[EstadoSolicitud] = None,
    ) -> List[SolicitudReposicion]: ...

    @abstractmethod
    def actualizar(self, solicitud: SolicitudReposicion) -> SolicitudReposicion: ...
