from sqlalchemy import Column, DateTime, DECIMAL, Enum, ForeignKey, Integer
from sqlalchemy.sql import func
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

    estado = Column(
        Enum("SOLICITADO", "EN_TRANSITO", "RECIBIDO", "CANCELADO"),
        nullable=False,
        default="SOLICITADO"
    )

    totalNeto = Column(DECIMAL(12, 2), nullable=False)
    totalIgv = Column(DECIMAL(12, 2), nullable=False)
    totalCompra = Column(DECIMAL(12, 2), nullable=False)