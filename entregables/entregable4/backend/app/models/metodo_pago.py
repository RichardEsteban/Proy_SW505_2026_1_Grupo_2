from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class MetodoPago(Base):
    __tablename__ = "metodopago"

    idMetodoPago = Column(Integer, primary_key=True, index=True)
    nombreMetodo = Column(String(50), nullable=False, unique=True)
    isActivo = Column(Boolean, nullable=False, default=True)

    ventas = relationship("Venta", back_populates="metodo_pago")
