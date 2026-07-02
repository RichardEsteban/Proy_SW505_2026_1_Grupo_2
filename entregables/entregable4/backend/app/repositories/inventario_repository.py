from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.inventario_ubicacion import InventarioUbicacion


class InventarioRepository:

    @staticmethod
    def obtener_todos(
        db: Session,
        id_ubicacion: int | None = None,
        id_producto: int | None = None,
        solo_bajo_minimo: bool = False,
    ) -> list[InventarioUbicacion]:
        stmt = (
            select(InventarioUbicacion)
            .options(
                joinedload(InventarioUbicacion.ubicacion),
                joinedload(InventarioUbicacion.producto),
            )
            .order_by(InventarioUbicacion.idUbicacion, InventarioUbicacion.idProducto)
        )

        if id_ubicacion is not None:
            stmt = stmt.where(InventarioUbicacion.idUbicacion == id_ubicacion)

        if id_producto is not None:
            stmt = stmt.where(InventarioUbicacion.idProducto == id_producto)

        if solo_bajo_minimo:
            stmt = stmt.where(
                InventarioUbicacion.stockDisponible <= InventarioUbicacion.stockMinimo
            )

        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def obtener_por_id(db: Session, id_inventario: int) -> InventarioUbicacion | None:
        stmt = (
            select(InventarioUbicacion)
            .options(
                joinedload(InventarioUbicacion.ubicacion),
                joinedload(InventarioUbicacion.producto),
            )
            .where(InventarioUbicacion.idInventario == id_inventario)
        )
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def obtener_por_ubicacion_producto(
        db: Session,
        id_ubicacion: int,
        id_producto: int,
    ) -> InventarioUbicacion | None:
        stmt = (
            select(InventarioUbicacion)
            .options(
                joinedload(InventarioUbicacion.ubicacion),
                joinedload(InventarioUbicacion.producto),
            )
            .where(
                InventarioUbicacion.idUbicacion == id_ubicacion,
                InventarioUbicacion.idProducto == id_producto,
            )
        )
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def guardar(db: Session, inventario: InventarioUbicacion) -> InventarioUbicacion:
        db.add(inventario)
        db.flush()
        db.refresh(inventario)
        return inventario
