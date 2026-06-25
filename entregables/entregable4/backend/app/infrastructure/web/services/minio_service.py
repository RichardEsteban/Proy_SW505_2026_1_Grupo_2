"""Servicio MinIO para almacenar PDFs/imágenes."""
from __future__ import annotations

import io
import logging
import os
from typing import Optional

from app.infrastructure.config.settings import Settings

log = logging.getLogger(__name__)


class MinioService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._client = None

        # Si está deshabilitado (modo local sin Docker), ni intenta conectar.
        if os.getenv("MINIO_ENABLED", "false").lower() not in ("1", "true", "yes"):
            log.info("MinIO deshabilitado (modo local). PDFs se guardan en /tmp.")
            return

        # Si está habilitado, intenta conectar
        try:
            from minio import Minio  # noqa: WPS433 (import local)
            self._client = Minio(
                settings.minio_endpoint,
                access_key=settings.minio_access_key,
                secret_key=settings.minio_secret_key,
                secure=settings.minio_secure,
            )
            self._asegurar_bucket()
        except Exception as e:
            log.warning("MinIO no disponible: %s", e)
            self._client = None

    def _asegurar_bucket(self) -> None:
        if not self._client:
            return
        try:
            if not self._client.bucket_exists(self.settings.minio_bucket):
                self._client.make_bucket(self.settings.minio_bucket)
        except Exception as e:
            log.warning("No se pudo crear bucket: %s", e)

    def subir(self, contenido: bytes, nombre: str, content_type: str = "application/pdf") -> str:
        if not self._client:
            # Fallback: devolver URL local (no se sube nada, pero no rompe)
            return f"/tmp/{nombre}"

        data = io.BytesIO(contenido)
        try:
            self._client.put_object(
                bucket_name=self.settings.minio_bucket,
                object_name=nombre,
                data=data,
                length=len(contenido),
                content_type=content_type,
            )
        except Exception as e:
            log.warning("Fallo al subir a MinIO, fallback a /tmp: %s", e)
            return f"/tmp/{nombre}"

        scheme = "https" if self.settings.minio_secure else "http"
        return f"{scheme}://{self.settings.minio_endpoint}/{self.settings.minio_bucket}/{nombre}"
