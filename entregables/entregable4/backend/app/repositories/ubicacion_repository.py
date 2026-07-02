from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ubicacion import Ubicacion


class UbicacionRepository:

    @staticmethod
    def obtener_todas(db: Session, incluir_inactivas: bool = True) -> list[Ubicacion]:
        stmt = select(Ubicacion).order_by(Ubicacion.idUbicacion)

        if not incluir_inactivas:
            stmt = stmt.where(Ubicacion.isActivo.is_(True))

        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def obtener_por_id(db: Session, id_ubicacion: int) -> Ubicacion | None:
        stmt = select(Ubicacion).where(Ubicacion.idUbicacion == id_ubicacion)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def obtener_por_nombre(db: Session, nombre: str) -> Ubicacion | None:
        stmt = select(Ubicacion).where(Ubicacion.nombreUbicacion == nombre)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def guardar(db: Session, ubicacion: Ubicacion) -> Ubicacion:
        db.add(ubicacion)
        db.flush()
        db.refresh(ubicacion)
        return ubicacion
