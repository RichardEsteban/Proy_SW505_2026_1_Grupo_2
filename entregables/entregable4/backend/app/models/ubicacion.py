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
    inventarios = relationship("InventarioUbicacion", back_populates="ubicacion")
    movimientos = relationship("MovimientoInventario", back_populates="ubicacion")
    alertas_stock = relationship("AlertaStock", back_populates="ubicacion")
    ventas = relationship("Venta", back_populates="ubicacion")
    ordenes_compra = relationship("OrdenCompra", back_populates="ubicacion_destino")
    reposiciones_origen = relationship(
        "SolicitudReposicion",
        foreign_keys="SolicitudReposicion.idUbicacionOrigen",
        back_populates="ubicacion_origen",
    )
    reposiciones_destino = relationship(
        "SolicitudReposicion",
        foreign_keys="SolicitudReposicion.idUbicacionDestino",
        back_populates="ubicacion_destino",
    )
