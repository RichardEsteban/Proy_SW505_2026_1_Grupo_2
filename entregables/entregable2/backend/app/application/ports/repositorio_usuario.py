from abc import ABC, abstractmethod
from typing import Optional
from app.domain.entities.usuario import Usuario

class IRepositorioUsuario(ABC):
    @abstractmethod
    def obtener_por_email(self, email: str) -> Optional[Usuario]:
        pass

    @abstractmethod
    def actualizar_password(self, usuario_id: int, nuevo_hash: str) -> None:
        pass
