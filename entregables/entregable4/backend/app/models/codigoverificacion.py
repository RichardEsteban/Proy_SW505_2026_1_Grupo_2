from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from app.db.base import Base


class CodigoVerificacion(Base):
    __tablename__ = "codigoverificacion"

    idCodigo = Column(Integer, primary_key=True, index=True)
    idUsuario = Column(Integer, ForeignKey("usuario.idUsuario"), nullable=False)

    codigo = Column(String(6), nullable=False)
    isUsado = Column(Boolean, nullable=False, default=False)
    fechaExpiracion = Column(DateTime, nullable=False)