from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.categoria import Categoria


class CategoriaRepository:

    @staticmethod
    def obtener_todas(db: Session, incluir_inactivas: bool = True) -> list[Categoria]:
        stmt = select(Categoria).order_by(Categoria.nombreCategoria)

        if not incluir_inactivas:
            stmt = stmt.where(Categoria.isActivo.is_(True))

        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def obtener_por_id(db: Session, id_categoria: int) -> Categoria | None:
        stmt = select(Categoria).where(Categoria.idCategoria == id_categoria)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def obtener_por_nombre(db: Session, id_empresa: int, nombre: str) -> Categoria | None:
        stmt = select(Categoria).where(
            Categoria.idEmpresa == id_empresa,
            Categoria.nombreCategoria == nombre,
        )
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def guardar(db: Session, categoria: Categoria) -> Categoria:
        db.add(categoria)
        db.flush()
        db.refresh(categoria)
        return categoria
