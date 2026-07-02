from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.usuario import Usuario


class UsuarioRepository:

    @staticmethod
    def obtener_todos(db: Session, incluir_inactivos: bool = True) -> list[Usuario]:
        stmt = (
            select(Usuario)
            .options(
                joinedload(Usuario.rol),
                joinedload(Usuario.ubicacion)
            )
            .order_by(Usuario.idUsuario)
        )

        if not incluir_inactivos:
            stmt = stmt.where(Usuario.isActivo.is_(True))

        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def obtener_por_correo(db: Session, correo: str) -> Usuario | None:
        stmt = (
            select(Usuario)
            .options(
                joinedload(Usuario.rol),
                joinedload(Usuario.ubicacion)
            )
            .where(func.lower(Usuario.correoElectronico) == str(correo).lower())
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

    @staticmethod
    def guardar(db: Session, usuario: Usuario) -> Usuario:
        db.add(usuario)
        db.flush()
        db.refresh(usuario)
        return usuario
