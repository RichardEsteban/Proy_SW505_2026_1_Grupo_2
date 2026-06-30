from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from app.db.base import Base


class InventarioUbicacion(Base):
    __tablename__ = "inventarioubicacion"

    idInventario = Column(Integer, primary_key=True, index=True)

    idUbicacion = Column(Integer, ForeignKey("ubicacion.idUbicacion"), nullable=False)
    idProducto = Column(Integer, ForeignKey("producto.idProducto"), nullable=False)

    stockDisponible = Column(Integer, nullable=False, default=0)
    stockMinimo = Column(Integer, nullable=False, default=0)

    __table_args__ = (
        UniqueConstraint("idUbicacion", "idProducto", name="uq_ubicacion_producto"),
    )