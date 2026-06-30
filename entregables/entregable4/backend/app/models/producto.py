from sqlalchemy import Boolean, Column, DECIMAL, ForeignKey, Integer, String
from app.db.base import Base


class Producto(Base):
    __tablename__ = "producto"

    idProducto = Column(Integer, primary_key=True, index=True)
    idEmpresa = Column(Integer, ForeignKey("empresa.idEmpresa"), nullable=False)

    codigoBarras = Column(String(50), nullable=False, unique=True)
    nombreProducto = Column(String(150), nullable=False)

    precioVenta = Column(DECIMAL(12, 2), nullable=False)
    porcentajeIgv = Column(DECIMAL(5, 2), nullable=False, default=18.00)

    isActivo = Column(Boolean, nullable=False, default=True)