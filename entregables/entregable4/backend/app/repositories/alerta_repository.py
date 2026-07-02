from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.alerta_stock import AlertaStock


class AlertaRepository:

    @staticmethod
    def obtener_todas(
        db: Session,
        id_ubicacion: int | None = None,
        estado: str | None = None,
    ) -> list[AlertaStock]:
        stmt = (
            select(AlertaStock)
            .options(
                joinedload(AlertaStock.ubicacion),
                joinedload(AlertaStock.producto),
            )
            .order_by(AlertaStock.fechaCreacion.desc())
        )

        if id_ubicacion is not None:
            stmt = stmt.where(AlertaStock.idUbicacion == id_ubicacion)

        if estado is not None:
            stmt = stmt.where(AlertaStock.estado == estado)

        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def obtener_por_id(db: Session, id_alerta: int) -> AlertaStock | None:
        stmt = (
            select(AlertaStock)
            .options(
                joinedload(AlertaStock.ubicacion),
                joinedload(AlertaStock.producto),
            )
            .where(AlertaStock.idAlerta == id_alerta)
        )
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def obtener_pendiente_por_producto(
        db: Session,
        id_ubicacion: int,
        id_producto: int,
        tipo_alerta: str,
    ) -> AlertaStock | None:
        stmt = select(AlertaStock).where(
            AlertaStock.idUbicacion == id_ubicacion,
            AlertaStock.idProducto == id_producto,
            AlertaStock.tipoAlerta == tipo_alerta,
            AlertaStock.estado == "PENDIENTE",
        )
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def guardar(db: Session, alerta: AlertaStock) -> AlertaStock:
        db.add(alerta)
        db.flush()
        db.refresh(alerta)
        return alerta
