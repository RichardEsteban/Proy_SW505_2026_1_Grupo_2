from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from app.db.base import Base


class Categoria(Base):
    __tablename__ = "categoria"

    idCategoria = Column(Integer, primary_key=True, index=True)
    idEmpresa = Column(Integer, ForeignKey("empresa.idEmpresa"), nullable=False)

    nombreCategoria = Column(String(100), nullable=False)
    descripcion = Column(String(200), nullable=True)
    isActivo = Column(Boolean, nullable=False, default=True)