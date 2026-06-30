from sqlalchemy import Column, DateTime, DECIMAL, ForeignKey, Integer, String
from sqlalchemy.sql import func
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