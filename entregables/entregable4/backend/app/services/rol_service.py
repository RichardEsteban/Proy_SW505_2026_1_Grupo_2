from sqlalchemy.orm import Session

from app.repositories.rol_repository import RolRepository
from app.schemas.rol_schema import RolResponse


class RolService:

    @staticmethod
    def listar(db: Session) -> list[RolResponse]:
        roles = RolRepository.obtener_todos(db)
        return [
            RolResponse(idRol=rol.idRol, nombreRol=rol.nombreRol)
            for rol in roles
        ]
