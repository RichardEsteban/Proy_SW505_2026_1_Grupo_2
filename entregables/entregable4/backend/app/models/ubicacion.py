from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Ubicacion(Base):
    __tablename__ = "ubicacion"

    idUbicacion = Column(Integer, primary_key=True, index=True)
    idEmpresa = Column(Integer, ForeignKey("empresa.idEmpresa"), nullable=False)

    nombreUbicacion = Column(String(150), nullable=False)
    tipoUbicacion = Column(Enum("ALMACEN", "SUCURSAL"), nullable=False)
    direccion = Column(String(255), nullable=False)

    isActivo = Column(Boolean, nullable=False, default=True)

    usuarios = relationship("Usuario", back_populates="ubicacion")