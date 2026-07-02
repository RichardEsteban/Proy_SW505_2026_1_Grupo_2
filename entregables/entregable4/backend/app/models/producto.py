from sqlalchemy import Boolean, Column, DECIMAL, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Producto(Base):
    __tablename__ = "producto"

    idProducto = Column(Integer, primary_key=True, index=True)
    idEmpresa = Column(Integer, ForeignKey("empresa.idEmpresa"), nullable=False)
    idCategoria = Column(Integer, ForeignKey("categoria.idCategoria"), nullable=True)
    codigoBarras = Column(String(50), nullable=False, unique=True, index=True)
    nombreProducto = Column(String(150), nullable=False, index=True)
    precioVenta = Column(DECIMAL(12, 2), nullable=False)
    porcentajeIgv = Column(DECIMAL(5, 2), nullable=False, default=18.00)
    isActivo = Column(Boolean, nullable=False, default=True)

    categoria = relationship("Categoria")
    inventarios = relationship("InventarioUbicacion", back_populates="producto")
    movimientos = relationship("MovimientoInventario", back_populates="producto")
    alertas_stock = relationship("AlertaStock", back_populates="producto")
    detalles_venta = relationship("DetalleVenta", back_populates="producto")
    detalles_orden_compra = relationship("DetalleOrdenCompra", back_populates="producto")
    detalles_solicitud_reposicion = relationship("DetalleSolicitudReposicion", back_populates="producto")
