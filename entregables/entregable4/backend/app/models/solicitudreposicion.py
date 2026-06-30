from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.sql import func
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
        Enum(
            "ENVIADO","EN_REVISION","ACEPTADO",
            "EN_TRANSITO","RECIBIDA","RECHAZADA","CANCELADA"
        ),
        nullable=False,
        default="ENVIADO"
    )

    observacion = Column(Text, nullable=True)
    fechaAperturaRevision = Column(DateTime, nullable=True)