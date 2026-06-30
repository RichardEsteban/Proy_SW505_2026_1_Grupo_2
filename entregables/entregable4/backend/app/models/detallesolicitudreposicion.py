from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from app.db.base import Base


class DetalleSolicitudReposicion(Base):
    __tablename__ = "detallesolicitudreposicion"

    idDetalleSolicitud = Column(Integer, primary_key=True, index=True)

    idSolicitud = Column(Integer, ForeignKey("solicitudreposicion.idSolicitud"), nullable=False)
    idProducto = Column(Integer, ForeignKey("producto.idProducto"), nullable=False)

    cantidadSolicitada = Column(Integer, nullable=False)
    cantidadDespachada = Column(Integer, nullable=False, default=0)

    __table_args__ = (
        UniqueConstraint("idSolicitud", "idProducto", name="uq_solicitud_producto"),
    )