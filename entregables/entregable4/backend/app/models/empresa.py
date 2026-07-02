from sqlalchemy import Boolean, CHAR, Column, DateTime, DECIMAL, Integer, String

from app.db.base import Base


class Empresa(Base):
    __tablename__ = "empresa"

    idEmpresa = Column(Integer, primary_key=True, index=True)
    nombreEmpresa = Column(String(150), nullable=False)
    isInicializado = Column(Boolean, nullable=False, default=False)
    fechaInicializacion = Column(DateTime, nullable=True)
    timer_revision_minutos = Column(Integer, nullable=False, default=60)
    igv_porcentaje = Column(DECIMAL(5, 2), nullable=False, default=18.00)
    moneda = Column(CHAR(3), nullable=False, default="PEN")