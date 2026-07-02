from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Cliente(Base):
    __tablename__ = "cliente"

    idCliente = Column(Integer, primary_key=True, index=True)
    tipoCliente = Column(Enum("PERSONA", "EMPRESA"), nullable=False)
    telefono = Column(String(20), nullable=True)
    correoElectronico = Column(String(150), nullable=True)
    isActivo = Column(Boolean, nullable=False, default=True)

    persona = relationship("Persona", back_populates="cliente", uselist=False, cascade="all, delete-orphan")
    empresa_cliente = relationship("EmpresaCliente", back_populates="cliente", uselist=False, cascade="all, delete-orphan")
    ventas = relationship("Venta", back_populates="cliente")


class Persona(Base):
    __tablename__ = "persona"

    idCliente = Column(Integer, ForeignKey("cliente.idCliente", ondelete="CASCADE"), primary_key=True)
    documentoIdentidad = Column(String(12), nullable=False, unique=True, index=True)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)

    cliente = relationship("Cliente", back_populates="persona")


class EmpresaCliente(Base):
    __tablename__ = "empresacliente"

    idCliente = Column(Integer, ForeignKey("cliente.idCliente", ondelete="CASCADE"), primary_key=True)
    identificacionFiscal = Column(String(11), nullable=False, unique=True, index=True)
    razonSocial = Column(String(150), nullable=False)
    direccionFiscal = Column(String(255), nullable=True)

    cliente = relationship("Cliente", back_populates="empresa_cliente")
