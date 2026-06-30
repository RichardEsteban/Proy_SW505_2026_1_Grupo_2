from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.usuario import Usuario


class UsuarioRepository:

    @staticmethod
    def obtener_por_correo(db: Session, correo: str) -> Usuario | None:
        stmt = (
            select(Usuario)
            .options(
                joinedload(Usuario.rol),
                joinedload(Usuario.ubicacion)
            )
            .where(Usuario.correoElectronico == correo)
        )

        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def obtener_por_id(db: Session, id_usuario: int) -> Usuario | None:
        stmt = (
            select(Usuario)
            .options(
                joinedload(Usuario.rol),
                joinedload(Usuario.ubicacion)
            )
            .where(Usuario.idUsuario == id_usuario)
        )

        return db.execute(stmt).scalar_one_or_none()