from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.venta import DetalleVenta, Venta


class VentaRepository:

    @staticmethod
    def obtener_todas(
        db: Session,
        id_ubicacion: int | None = None,
        id_usuario: int | None = None,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        limite: int = 100,
    ) -> list[Venta]:
        stmt = (
            select(Venta)
            .options(
                joinedload(Venta.ubicacion),
                joinedload(Venta.usuario),
                joinedload(Venta.cliente),
                joinedload(Venta.metodo_pago),
                joinedload(Venta.detalles).joinedload(DetalleVenta.producto),
            )
            .order_by(Venta.fechaHora.desc(), Venta.idVenta.desc())
            .limit(limite)
        )

        if id_ubicacion is not None:
            stmt = stmt.where(Venta.idUbicacion == id_ubicacion)

        if id_usuario is not None:
            stmt = stmt.where(Venta.idUsuario == id_usuario)

        if desde is not None:
            stmt = stmt.where(Venta.fechaHora >= desde)

        if hasta is not None:
            stmt = stmt.where(Venta.fechaHora <= hasta)

        return list(db.execute(stmt).unique().scalars().all())

    @staticmethod
    def obtener_por_id(db: Session, id_venta: int) -> Venta | None:
        stmt = (
            select(Venta)
            .options(
                joinedload(Venta.ubicacion),
                joinedload(Venta.usuario),
                joinedload(Venta.cliente),
                joinedload(Venta.metodo_pago),
                joinedload(Venta.detalles).joinedload(DetalleVenta.producto),
            )
            .where(Venta.idVenta == id_venta)
        )
        return db.execute(stmt).unique().scalar_one_or_none()

    @staticmethod
    def guardar(db: Session, venta: Venta) -> Venta:
        db.add(venta)
        db.flush()
        db.refresh(venta)
        return venta
