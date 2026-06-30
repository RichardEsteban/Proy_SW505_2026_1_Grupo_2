from sqlalchemy import Column, ForeignKey, Integer, DECIMAL, UniqueConstraint
from app.db.base import Base


class DetalleOrdenCompra(Base):
    __tablename__ = "detalleordencompra"

    idDetalleOrden = Column(Integer, primary_key=True, index=True)

    idOrdenCompra = Column(Integer, ForeignKey("ordencompra.idOrdenCompra"), nullable=False)
    idProducto = Column(Integer, ForeignKey("producto.idProducto"), nullable=False)

    cantidadPedida = Column(Integer, nullable=False)
    cantidadRecibida = Column(Integer, nullable=False, default=0)
    precioCompraUnitario = Column(DECIMAL(12, 2), nullable=False)

    __table_args__ = (
        UniqueConstraint("idOrdenCompra", "idProducto", name="uq_orden_producto"),
    )