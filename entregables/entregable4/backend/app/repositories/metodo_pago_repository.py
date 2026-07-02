from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.metodo_pago import MetodoPago


class MetodoPagoRepository:

    @staticmethod
    def obtener_todos(db: Session, incluir_inactivos: bool = False) -> list[MetodoPago]:
        stmt = select(MetodoPago).order_by(MetodoPago.nombreMetodo)
        if not incluir_inactivos:
            stmt = stmt.where(MetodoPago.isActivo == True)
        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def obtener_por_id(db: Session, id_metodo_pago: int) -> MetodoPago | None:
        stmt = select(MetodoPago).where(MetodoPago.idMetodoPago == id_metodo_pago)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def obtener_por_nombre(db: Session, nombre_metodo: str) -> MetodoPago | None:
        stmt = select(MetodoPago).where(MetodoPago.nombreMetodo == nombre_metodo)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def guardar(db: Session, metodo_pago: MetodoPago) -> MetodoPago:
        db.add(metodo_pago)
        db.flush()
        db.refresh(metodo_pago)
        return metodo_pago
