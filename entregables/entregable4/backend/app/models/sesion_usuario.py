from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class SesionUsuario(Base):
    __tablename__ = "sesionusuario"

    idSesion = Column(Integer, primary_key=True, index=True)
    idUsuario = Column(Integer, ForeignKey("usuario.idUsuario"), nullable=False, index=True)
    tokenId = Column(String(80), nullable=False, unique=True, index=True)
    isActiva = Column(Boolean, nullable=False, default=True)
    fechaInicio = Column(DateTime, nullable=False, server_default=func.now())
    fechaUltimaActividad = Column(DateTime, nullable=False, server_default=func.now())
    fechaCierre = Column(DateTime, nullable=True)
    motivoCierre = Column(String(80), nullable=True)

    usuario = relationship("Usuario", back_populates="sesiones")
