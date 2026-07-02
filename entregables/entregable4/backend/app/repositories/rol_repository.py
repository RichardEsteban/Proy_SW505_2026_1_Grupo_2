from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.rol import Rol


class RolRepository:

    @staticmethod
    def obtener_todos(db: Session) -> list[Rol]:
        stmt = select(Rol).order_by(Rol.idRol)
        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def obtener_por_id(db: Session, id_rol: int) -> Rol | None:
        stmt = select(Rol).where(Rol.idRol == id_rol)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def obtener_por_nombre(db: Session, nombre_rol: str) -> Rol | None:
        stmt = select(Rol).where(Rol.nombreRol == nombre_rol)
        return db.execute(stmt).scalar_one_or_none()
