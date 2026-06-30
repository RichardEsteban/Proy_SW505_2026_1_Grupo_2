from sqlalchemy import Column, ForeignKey, Integer, String
from app.db.base import Base


class Persona(Base):
    __tablename__ = "persona"

    idCliente = Column(Integer, ForeignKey("cliente.idCliente"), primary_key=True)

    documentoIdentidad = Column(String(12), nullable=False, unique=True)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)