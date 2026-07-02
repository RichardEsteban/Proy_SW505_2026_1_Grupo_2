from sqlalchemy import Column, DateTime, DECIMAL, Enum, ForeignKey, Integer, CheckConstraint, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class OrdenCompra(Base):
    __tablename__ = "ordencompra"

    idOrdenCompra = Column(Integer, primary_key=True, index=True)
    idProveedor = Column(Integer, ForeignKey("proveedor.idProveedor"), nullable=False)
    idUbicacionDestino = Column(Integer, ForeignKey("ubicacion.idUbicacion"), nullable=False)
    idUsuarioComprador = Column(Integer, ForeignKey("usuario.idUsuario"), nullable=False)
    idUsuarioReceptor = Column(Integer, ForeignKey("usuario.idUsuario"), nullable=True)

    fechaPedido = Column(DateTime, nullable=False, server_default=func.now())
    fechaRecepcion = Column(DateTime, nullable=True)
    estado = Column(Enum("SOLICITADO", "EN_TRANSITO", "RECIBIDO", "CANCELADO"), nullable=False, default="SOLICITADO")
    totalNeto = Column(DECIMAL(12, 2), nullable=False)
    totalIgv = Column(DECIMAL(12, 2), nullable=False)
    totalCompra = Column(DECIMAL(12, 2), nullable=False)

    proveedor = relationship("Proveedor", back_populates="ordenes_compra")
    ubicacion_destino = relationship("Ubicacion", back_populates="ordenes_compra")
    usuario_comprador = relationship("Usuario", foreign_keys=[idUsuarioComprador], back_populates="ordenes_compra_compradas")
    usuario_receptor = relationship("Usuario", foreign_keys=[idUsuarioReceptor], back_populates="ordenes_compra_recibidas")
    detalles = relationship("DetalleOrdenCompra", back_populates="orden_compra", cascade="all, delete-orphan")


class DetalleOrdenCompra(Base):
    __tablename__ = "detalleordencompra"

    idDetalleOrden = Column(Integer, primary_key=True, index=True)
    idOrdenCompra = Column(Integer, ForeignKey("ordencompra.idOrdenCompra", ondelete="CASCADE"), nullable=False)
    idProducto = Column(Integer, ForeignKey("producto.idProducto"), nullable=False)
    cantidadPedida = Column(Integer, nullable=False)
    cantidadRecibida = Column(Integer, nullable=False, default=0)
    precioCompraUnitario = Column(DECIMAL(12, 2), nullable=False)

    orden_compra = relationship("OrdenCompra", back_populates="detalles")
    producto = relationship("Producto", back_populates="detalles_orden_compra")

    __table_args__ = (
        UniqueConstraint("idOrdenCompra", "idProducto", name="UNIQUE_orden_producto"),
        CheckConstraint("cantidadPedida > 0", name="CHK_compra_cantidad"),
    )
