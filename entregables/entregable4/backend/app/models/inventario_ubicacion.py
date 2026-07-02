from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base import Base


class InventarioUbicacion(Base):
    __tablename__ = "inventarioubicacion"

    idInventario = Column(Integer, primary_key=True, index=True)
    idUbicacion = Column(Integer, ForeignKey("ubicacion.idUbicacion"), nullable=False)
    idProducto = Column(Integer, ForeignKey("producto.idProducto"), nullable=False)
    stockDisponible = Column(Integer, nullable=False, default=0)
    stockMinimo = Column(Integer, nullable=False, default=0)

    ubicacion = relationship("Ubicacion", back_populates="inventarios")
    producto = relationship("Producto", back_populates="inventarios")

    __table_args__ = (
        UniqueConstraint("idUbicacion", "idProducto", name="uq_inventario_ubicacion_producto"),
        CheckConstraint("stockDisponible >= 0", name="chk_stock_disponible"),
        CheckConstraint("stockMinimo >= 0", name="chk_stock_minimo"),
    )
