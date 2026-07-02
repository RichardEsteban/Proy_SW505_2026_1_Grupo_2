from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.producto import Producto


class ProductoRepository:

    @staticmethod
    def obtener_todos(db: Session, incluir_inactivos: bool = True) -> list[Producto]:
        stmt = select(Producto).order_by(Producto.nombreProducto)

        if not incluir_inactivos:
            stmt = stmt.where(Producto.isActivo.is_(True))

        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def obtener_por_id(db: Session, id_producto: int) -> Producto | None:
        stmt = select(Producto).where(Producto.idProducto == id_producto)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def obtener_por_codigo_barras(db: Session, codigo_barras: str) -> Producto | None:
        stmt = select(Producto).where(Producto.codigoBarras == codigo_barras)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def guardar(db: Session, producto: Producto) -> Producto:
        db.add(producto)
        db.flush()
        db.refresh(producto)
        return producto
