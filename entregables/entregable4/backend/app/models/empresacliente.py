from sqlalchemy import Column, ForeignKey, Integer, String
from app.db.base import Base


class EmpresaCliente(Base):
    __tablename__ = "empresacliente"

    idCliente = Column(Integer, ForeignKey("cliente.idCliente"), primary_key=True)

    identificacionFiscal = Column(String(11), nullable=False, unique=True)
    razonSocial = Column(String(150), nullable=False)
    direccionFiscal = Column(String(255), nullable=True)