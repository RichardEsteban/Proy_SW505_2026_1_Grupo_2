from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, CheckConstraint, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class MovimientoInventario(Base):
    __tablename__ = "movimientoinventario"

    idMovimiento = Column(Integer, primary_key=True, index=True)
    idUbicacion = Column(Integer, ForeignKey("ubicacion.idUbicacion"), nullable=False)
    idProducto = Column(Integer, ForeignKey("producto.idProducto"), nullable=False)
    idUsuario = Column(Integer, ForeignKey("usuario.idUsuario"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    tipoMovimiento = Column(Enum("INGRESO", "SALIDA"), nullable=False)
    motivoMovimiento = Column(
        Enum(
            "VENTA",
            "COMPRA_PROVEEDOR",
            "REPOSICION_ENVIADA",
            "REPOSICION_RECIBIDA",
            "MERMA",
            "AJUSTE",
        ),
        nullable=False,
    )
    tipoReferencia = Column(Enum("VENTA", "ORDEN_COMPRA", "SOLICITUD_REPOSICION"), nullable=True)
    idReferencia = Column(Integer, nullable=True)
    fechaHora = Column(DateTime, nullable=False, server_default=func.now())

    ubicacion = relationship("Ubicacion", back_populates="movimientos")
    producto = relationship("Producto", back_populates="movimientos")
    usuario = relationship("Usuario", back_populates="movimientos_inventario")

    __table_args__ = (
        CheckConstraint("cantidad > 0", name="chk_movimiento_cantidad_positiva"),
    )
