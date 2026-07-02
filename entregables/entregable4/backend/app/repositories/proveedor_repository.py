from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.proveedor import Proveedor


class ProveedorRepository:

    @staticmethod
    def obtener_todos(db: Session, incluir_inactivos: bool = True) -> list[Proveedor]:
        stmt = select(Proveedor).order_by(Proveedor.razonSocial)

        if not incluir_inactivos:
            stmt = stmt.where(Proveedor.isActivo.is_(True))

        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def obtener_por_id(db: Session, id_proveedor: int) -> Proveedor | None:
        stmt = select(Proveedor).where(Proveedor.idProveedor == id_proveedor)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def obtener_por_identificacion(db: Session, identificacion_fiscal: str) -> Proveedor | None:
        stmt = select(Proveedor).where(Proveedor.identificacionFiscal == identificacion_fiscal)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def guardar(db: Session, proveedor: Proveedor) -> Proveedor:
        db.add(proveedor)
        db.flush()
        db.refresh(proveedor)
        return proveedor
