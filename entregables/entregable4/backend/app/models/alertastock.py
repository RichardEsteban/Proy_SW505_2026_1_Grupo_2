from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer
from sqlalchemy.sql import func
from app.db.base import Base


class AlertaStock(Base):
    __tablename__ = "alertastock"

    idAlerta = Column(Integer, primary_key=True, index=True)

    idUbicacion = Column(Integer, ForeignKey("ubicacion.idUbicacion"), nullable=False)
    idProducto = Column(Integer, ForeignKey("producto.idProducto"), nullable=False)

    tipoAlerta = Column(Enum("STOCK_MINIMO", "STOCK_AGOTADO"), nullable=False)

    cantidadActual = Column(Integer, nullable=False)
    stockReferencia = Column(Integer, nullable=False)

    estado = Column(
        Enum("PENDIENTE", "LEIDA"),
        nullable=False,
        default="PENDIENTE"
    )

    fechaCreacion = Column(DateTime, nullable=False, server_default=func.now())
    fechaLeida = Column(DateTime, nullable=True)