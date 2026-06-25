"""Puerto: Generador de PDF (para comprobantes)."""
from __future__ import annotations

from abc import ABC, abstractmethod


class GeneradorPDF(ABC):
    @abstractmethod
    def generar_comprobante_venta(self, venta_id: int) -> bytes: ...

    @abstractmethod
    def guardar(self, contenido: bytes, nombre_archivo: str) -> str:
        """Sube el PDF y devuelve la URL pública."""
        ...
