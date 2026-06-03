import re
from app.application.ports.repositorio_usuario import IRepositorioUsuario
from app.domain.entities.usuario import Usuario
from app.domain.exceptions.credenciales_invalidas import CredencialesInvalidas

class GestionAccesosUseCase:
    def __init__(self, repo: IRepositorioUsuario):
        self.repo = repo

    def autenticar(self, email: str, password_plano: str) -> Usuario:
        usuario = self.repo.obtener_por_email(email)
        
        if not usuario or usuario.password_hash != password_plano or not usuario.activo:
            raise CredencialesInvalidas("Email o contraseña incorrectos.")
            
        return usuario

    def cambiar_password(self, usuario_id: int, password_actual: str, nueva_password: str, confirmacion: str) -> None:
        if nueva_password != confirmacion:
            raise ValueError("La confirmación de la contraseña no coincide.")
            
        if len(nueva_password) < 8 or not re.search(r"\d", nueva_password):
            raise ValueError("La contraseña debe tener al menos 8 caracteres y un número.")


        self.repo.actualizar_password(usuario_id, nueva_password)