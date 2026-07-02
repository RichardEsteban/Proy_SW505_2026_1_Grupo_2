from sqlalchemy import Column, DateTime, DECIMAL, ForeignKey, Integer, String, CheckConstraint, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class Venta(Base):
    __tablename__ = "venta"

    idVenta = Column(Integer, primary_key=True, index=True)
    idUbicacion = Column(Integer, ForeignKey("ubicacion.idUbicacion"), nullable=False)
    idUsuario = Column(Integer, ForeignKey("usuario.idUsuario"), nullable=False)
    idCliente = Column(Integer, ForeignKey("cliente.idCliente"), nullable=True)
    idMetodoPago = Column(Integer, ForeignKey("metodopago.idMetodoPago"), nullable=False)

    fechaHora = Column(DateTime, nullable=False, server_default=func.now())
    subtotalVenta = Column(DECIMAL(12, 2), nullable=False)
    totalIgv = Column(DECIMAL(12, 2), nullable=False)
    totalVenta = Column(DECIMAL(12, 2), nullable=False)
    pdf_url = Column(String(255), nullable=True)

    ubicacion = relationship("Ubicacion", back_populates="ventas")
    usuario = relationship("Usuario", back_populates="ventas")
    cliente = relationship("Cliente", back_populates="ventas")
    metodo_pago = relationship("MetodoPago", back_populates="ventas")
    detalles = relationship("DetalleVenta", back_populates="venta", cascade="all, delete-orphan")


class DetalleVenta(Base):
    __tablename__ = "detalleventa"

    idDetalleVenta = Column(Integer, primary_key=True, index=True)
    idVenta = Column(Integer, ForeignKey("venta.idVenta", ondelete="CASCADE"), nullable=False)
    idProducto = Column(Integer, ForeignKey("producto.idProducto"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precioUnitarioFacturado = Column(DECIMAL(12, 2), nullable=False)
    igvAplicado = Column(DECIMAL(12, 2), nullable=False)
    subtotal = Column(DECIMAL(12, 2), nullable=False)

    venta = relationship("Venta", back_populates="detalles")
    producto = relationship("Producto", back_populates="detalles_venta")

    __table_args__ = (
        UniqueConstraint("idVenta", "idProducto", name="UNIQUE_venta_producto"),
        CheckConstraint("cantidad > 0", name="CHK_venta_cantidad"),
    )
