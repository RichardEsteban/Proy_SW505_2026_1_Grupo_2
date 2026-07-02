from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func

from app.db.base import Base


class CodigoVerificacion(Base):
    __tablename__ = "codigoverificacion"

    idCodigo = Column(Integer, primary_key=True, index=True)
    idUsuario = Column(Integer, ForeignKey("usuario.idUsuario"), nullable=False, index=True)
    codigoHash = Column(String(255), nullable=True)
    isUsado = Column(Boolean, nullable=False, default=False)
    intentos = Column(Integer, nullable=False, default=0)
    fechaCreacion = Column(DateTime, nullable=False, server_default=func.now())
    fechaExpiracion = Column(DateTime, nullable=False)
    fechaUso = Column(DateTime, nullable=True)
