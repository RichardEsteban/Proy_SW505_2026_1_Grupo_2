"""Caso de uso: Evaluar (aprobar/rechazar) una solicitud de reposición."""
from __future__ import annotations

from app.application.ports.repositorio_solicitud import RepositorioSolicitud
from app.domain.exceptions.estado_invalido import EstadoInvalidoError


class EvaluarSolicitud:
    def __init__(self, repo_solicitudes: RepositorioSolicitud) -> None:
        self._solicitudes = repo_solicitudes

    def aprobar(self, solicitud_id: int, evaluador_id: int) -> None:
        sol = self._solicitudes.obtener_por_id(solicitud_id)
        if sol is None:
            raise EstadoInvalidoError(f"Solicitud {solicitud_id} no existe")
        sol.aprobar(evaluador_id)
        self._solicitudes.actualizar(sol)

    def rechazar(self, solicitud_id: int, evaluador_id: int, motivo: str) -> None:
        sol = self._solicitudes.obtener_por_id(solicitud_id)
        if sol is None:
            raise EstadoInvalidoError(f"Solicitud {solicitud_id} no existe")
        sol.rechazar(evaluador_id, motivo)
        self._solicitudes.actualizar(sol)
