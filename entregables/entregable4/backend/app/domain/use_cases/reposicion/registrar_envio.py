"""Caso de uso: Registrar envío de una solicitud aprobada."""
from __future__ import annotations

from app.application.ports.repositorio_solicitud import RepositorioSolicitud
from app.domain.exceptions.estado_invalido import EstadoInvalidoError


class RegistrarEnvio:
    def __init__(self, repo_solicitudes: RepositorioSolicitud) -> None:
        self._solicitudes = repo_solicitudes

    def ejecutar(self, solicitud_id: int) -> None:
        sol = self._solicitudes.obtener_por_id(solicitud_id)
        if sol is None:
            raise EstadoInvalidoError(f"Solicitud {solicitud_id} no existe")
        sol.enviar()
        self._solicitudes.actualizar(sol)
