from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.empresa import Empresa


class EmpresaRepository:

    @staticmethod
    def obtener_primera(db: Session) -> Empresa | None:
        stmt = select(Empresa).limit(1)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def guardar(db: Session, empresa: Empresa) -> Empresa:
        db.add(empresa)
        db.flush()
        db.refresh(empresa)
        return empresa
