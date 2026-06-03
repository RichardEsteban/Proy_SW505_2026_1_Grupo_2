from app.application.ports.repositorio_usuario import IRepositorioUsuario
from app.domain.entities.usuario import Usuario
from typing import Optional, List

class FakeRepositorioUsuario(IRepositorioUsuario):
    def __init__(self, usuarios: List[Usuario] = None):
        self._usuarios = usuarios or []

    def obtener_por_email(self, email: str) -> Optional[Usuario]:
        return next((u for u in self._usuarios if u.email == email), None)

    def actualizar_password(self, usuario_id: int, nuevo_hash: str) -> None:
        for u in self._usuarios:
            if u.id == usuario_id:
                u.password_hash = nuevo_hash
                return
