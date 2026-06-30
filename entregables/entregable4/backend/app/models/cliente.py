from sqlalchemy import Column, Enum, Integer, String
from app.db.base import Base


class Cliente(Base):
    __tablename__ = "cliente"

    idCliente = Column(Integer, primary_key=True, index=True)
    tipoCliente = Column(Enum("PERSONA", "EMPRESA"), nullable=False)

    telefono = Column(String(20), nullable=True)
    correoElectronico = Column(String(150), nullable=True)