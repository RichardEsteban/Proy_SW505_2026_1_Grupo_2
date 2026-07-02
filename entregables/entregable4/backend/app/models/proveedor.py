from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Proveedor(Base):
    __tablename__ = "proveedor"

    idProveedor = Column(Integer, primary_key=True, index=True)
    idEmpresa = Column(Integer, ForeignKey("empresa.idEmpresa"), nullable=False)
    identificacionFiscal = Column(String(11), nullable=False, unique=True, index=True)
    razonSocial = Column(String(150), nullable=False)
    contactoNombre = Column(String(100), nullable=True)
    telefono = Column(String(20), nullable=True)
    correoElectronico = Column(String(150), nullable=True)
    direccion = Column(String(255), nullable=True)
    isActivo = Column(Boolean, nullable=False, default=True)

    ordenes_compra = relationship("OrdenCompra", back_populates="proveedor")
