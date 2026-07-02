from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Text, CheckConstraint, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class SolicitudReposicion(Base):
    __tablename__ = "solicitudreposicion"

    idSolicitud = Column(Integer, primary_key=True, index=True)
    idUbicacionOrigen = Column(Integer, ForeignKey("ubicacion.idUbicacion"), nullable=False)
    idUbicacionDestino = Column(Integer, ForeignKey("ubicacion.idUbicacion"), nullable=False)
    idUsuarioSolicitante = Column(Integer, ForeignKey("usuario.idUsuario"), nullable=False)
    idUsuarioDespachador = Column(Integer, ForeignKey("usuario.idUsuario"), nullable=True)
    idUsuarioReceptor = Column(Integer, ForeignKey("usuario.idUsuario"), nullable=True)

    fechaSolicitud = Column(DateTime, nullable=False, server_default=func.now())
    fechaDespacho = Column(DateTime, nullable=True)
    fechaRecepcion = Column(DateTime, nullable=True)
    estado = Column(
        Enum("ENVIADO", "EN_REVISION", "ACEPTADO", "EN_TRANSITO", "RECIBIDA", "RECHAZADA", "CANCELADA"),
        nullable=False,
        default="ENVIADO",
    )
    observacion = Column(Text, nullable=True)
    fechaAperturaRevision = Column(DateTime, nullable=True)

    ubicacion_origen = relationship("Ubicacion", foreign_keys=[idUbicacionOrigen], back_populates="reposiciones_origen")
    ubicacion_destino = relationship("Ubicacion", foreign_keys=[idUbicacionDestino], back_populates="reposiciones_destino")
    usuario_solicitante = relationship("Usuario", foreign_keys=[idUsuarioSolicitante], back_populates="reposiciones_solicitadas")
    usuario_despachador = relationship("Usuario", foreign_keys=[idUsuarioDespachador], back_populates="reposiciones_despachadas")
    usuario_receptor = relationship("Usuario", foreign_keys=[idUsuarioReceptor], back_populates="reposiciones_recibidas")
    detalles = relationship("DetalleSolicitudReposicion", back_populates="solicitud_reposicion", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("idUbicacionOrigen <> idUbicacionDestino", name="CHK_reposicion_origen_destino"),
    )


class DetalleSolicitudReposicion(Base):
    __tablename__ = "detallesolicitudreposicion"

    idDetalleSolicitud = Column(Integer, primary_key=True, index=True)
    idSolicitud = Column(Integer, ForeignKey("solicitudreposicion.idSolicitud", ondelete="CASCADE"), nullable=False)
    idProducto = Column(Integer, ForeignKey("producto.idProducto"), nullable=False)
    cantidadSolicitada = Column(Integer, nullable=False)
    cantidadDespachada = Column(Integer, nullable=False, default=0)

    solicitud_reposicion = relationship("SolicitudReposicion", back_populates="detalles")
    producto = relationship("Producto", back_populates="detalles_solicitud_reposicion")

    __table_args__ = (
        UniqueConstraint("idSolicitud", "idProducto", name="UNIQUE_solicitud_producto"),
        CheckConstraint("cantidadSolicitada > 0", name="CHK_reposicion_cantidad"),
    )
