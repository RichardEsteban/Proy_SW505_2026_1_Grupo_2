from sqlalchemy import Column, ForeignKey, Integer, DECIMAL, UniqueConstraint
from app.db.base import Base


class DetalleVenta(Base):
    __tablename__ = "detalleventa"

    idDetalleVenta = Column(Integer, primary_key=True, index=True)

    idVenta = Column(Integer, ForeignKey("venta.idVenta"), nullable=False)
    idProducto = Column(Integer, ForeignKey("producto.idProducto"), nullable=False)

    cantidad = Column(Integer, nullable=False)
    precioUnitarioFacturado = Column(DECIMAL(12, 2), nullable=False)
    igvAplicado = Column(DECIMAL(12, 2), nullable=False)
    subtotal = Column(DECIMAL(12, 2), nullable=False)

    __table_args__ = (
        UniqueConstraint("idVenta", "idProducto", name="uq_venta_producto"),
    )