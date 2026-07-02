from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.movimiento_inventario import MovimientoInventario


class MovimientoRepository:

    @staticmethod
    def obtener_todos(
        db: Session,
        id_ubicacion: int | None = None,
        id_producto: int | None = None,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        limite: int = 100,
    ) -> list[MovimientoInventario]:
        stmt = (
            select(MovimientoInventario)
            .options(
                joinedload(MovimientoInventario.ubicacion),
                joinedload(MovimientoInventario.producto),
                joinedload(MovimientoInventario.usuario),
            )
            .order_by(MovimientoInventario.fechaHora.desc())
            .limit(limite)
        )

        if id_ubicacion is not None:
            stmt = stmt.where(MovimientoInventario.idUbicacion == id_ubicacion)

        if id_producto is not None:
            stmt = stmt.where(MovimientoInventario.idProducto == id_producto)

        if desde is not None:
            stmt = stmt.where(MovimientoInventario.fechaHora >= desde)

        if hasta is not None:
            stmt = stmt.where(MovimientoInventario.fechaHora <= hasta)

        return list(db.execute(stmt).scalars().all())


    @staticmethod
    def obtener_por_id(db: Session, id_movimiento: int) -> MovimientoInventario | None:
        stmt = (
            select(MovimientoInventario)
            .options(
                joinedload(MovimientoInventario.ubicacion),
                joinedload(MovimientoInventario.producto),
                joinedload(MovimientoInventario.usuario),
            )
            .where(MovimientoInventario.idMovimiento == id_movimiento)
        )
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def guardar(db: Session, movimiento: MovimientoInventario) -> MovimientoInventario:
        db.add(movimiento)
        db.flush()
        db.refresh(movimiento)
        return movimiento
