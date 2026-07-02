from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from app.models.cliente import Cliente, EmpresaCliente, Persona


class ClienteRepository:

    @staticmethod
    def obtener_todos(db: Session, incluir_inactivos: bool = False) -> list[Cliente]:
        stmt = (
            select(Cliente)
            .options(joinedload(Cliente.persona), joinedload(Cliente.empresa_cliente))
            .outerjoin(Persona, Cliente.idCliente == Persona.idCliente)
            .outerjoin(EmpresaCliente, Cliente.idCliente == EmpresaCliente.idCliente)
            .order_by(Persona.apellidos, Persona.nombres, EmpresaCliente.razonSocial)
        )
        if not incluir_inactivos:
            stmt = stmt.where(Cliente.isActivo.is_(True))
        return list(db.execute(stmt).unique().scalars().all())

    @staticmethod
    def obtener_por_id(db: Session, id_cliente: int) -> Cliente | None:
        stmt = (
            select(Cliente)
            .options(joinedload(Cliente.persona), joinedload(Cliente.empresa_cliente))
            .where(Cliente.idCliente == id_cliente)
        )
        return db.execute(stmt).unique().scalar_one_or_none()

    @staticmethod
    def obtener_por_documento(db: Session, documento: str) -> Cliente | None:
        stmt = (
            select(Cliente)
            .options(joinedload(Cliente.persona), joinedload(Cliente.empresa_cliente))
            .outerjoin(Persona, Cliente.idCliente == Persona.idCliente)
            .outerjoin(EmpresaCliente, Cliente.idCliente == EmpresaCliente.idCliente)
            .where(or_(Persona.documentoIdentidad == documento, EmpresaCliente.identificacionFiscal == documento))
        )
        return db.execute(stmt).unique().scalar_one_or_none()

    @staticmethod
    def guardar(db: Session, cliente: Cliente) -> Cliente:
        db.add(cliente)
        db.flush()
        db.refresh(cliente)
        return cliente
