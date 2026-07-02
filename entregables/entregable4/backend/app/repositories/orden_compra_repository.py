from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.orden_compra import DetalleOrdenCompra, OrdenCompra


class OrdenCompraRepository:

    @staticmethod
    def obtener_todas(
        db: Session,
        id_proveedor: int | None = None,
        id_ubicacion_destino: int | None = None,
        estado: str | None = None,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        limite: int = 100,
    ) -> list[OrdenCompra]:
        stmt = (
            select(OrdenCompra)
            .options(
                joinedload(OrdenCompra.proveedor),
                joinedload(OrdenCompra.ubicacion_destino),
                joinedload(OrdenCompra.usuario_comprador),
                joinedload(OrdenCompra.usuario_receptor),
                joinedload(OrdenCompra.detalles).joinedload(DetalleOrdenCompra.producto),
            )
            .order_by(OrdenCompra.fechaPedido.desc(), OrdenCompra.idOrdenCompra.desc())
            .limit(limite)
        )

        if id_proveedor is not None:
            stmt = stmt.where(OrdenCompra.idProveedor == id_proveedor)
        if id_ubicacion_destino is not None:
            stmt = stmt.where(OrdenCompra.idUbicacionDestino == id_ubicacion_destino)
        if estado is not None:
            stmt = stmt.where(OrdenCompra.estado == estado)
        if desde is not None:
            stmt = stmt.where(OrdenCompra.fechaPedido >= desde)
        if hasta is not None:
            stmt = stmt.where(OrdenCompra.fechaPedido <= hasta)

        return list(db.execute(stmt).unique().scalars().all())

    @staticmethod
    def obtener_por_id(db: Session, id_orden_compra: int) -> OrdenCompra | None:
        stmt = (
            select(OrdenCompra)
            .options(
                joinedload(OrdenCompra.proveedor),
                joinedload(OrdenCompra.ubicacion_destino),
                joinedload(OrdenCompra.usuario_comprador),
                joinedload(OrdenCompra.usuario_receptor),
                joinedload(OrdenCompra.detalles).joinedload(DetalleOrdenCompra.producto),
            )
            .where(OrdenCompra.idOrdenCompra == id_orden_compra)
        )
        return db.execute(stmt).unique().scalar_one_or_none()

    @staticmethod
    def guardar(db: Session, orden_compra: OrdenCompra) -> OrdenCompra:
        db.add(orden_compra)
        db.flush()
        db.refresh(orden_compra)
        return orden_compra
