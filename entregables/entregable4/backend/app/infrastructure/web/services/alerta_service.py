"""Servicio de Alertas: tareas programadas, WebSocket pubsub, etc.

En este scaffold sólo exponemos el wrapper que el caso de uso invoca.
"""
from __future__ import annotations

import logging
from typing import List

log = logging.getLogger(__name__)


class AlertaService:
    def __init__(self) -> None:
        self._subscribers: List[callable] = []

    def suscribir(self, callback: callable) -> None:
        self._subscribers.append(callback)

    def publicar(self, evento: dict) -> None:
        log.info("AlertaService.publish: %s", evento)
        for cb in self._subscribers:
            try:
                cb(evento)
            except Exception as e:
                log.exception("Error en subscriber: %s", e)
