from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Rol(Base):
    __tablename__ = "rol"

    idRol = Column(Integer, primary_key=True, index=True)
    nombreRol = Column(String(50), nullable=False, unique=True)

    usuarios = relationship("Usuario", back_populates="rol")