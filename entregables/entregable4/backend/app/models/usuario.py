from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class Usuario(Base):
    __tablename__ = "usuario"

    idUsuario = Column(Integer, primary_key=True, index=True)
    idUbicacion = Column(Integer, ForeignKey("ubicacion.idUbicacion"), nullable=False)
    idRol = Column(Integer, ForeignKey("rol.idRol"), nullable=False)

    correoElectronico = Column(String(150), nullable=False, unique=True, index=True)
    contrasenaHash = Column(String(255), nullable=False)

    isActivo = Column(Boolean, nullable=False, default=True)
    isContrasenaTemporal = Column(Boolean, nullable=False, default=True)
    fechaCreacion = Column(DateTime, nullable=False, server_default=func.now())

    rol = relationship("Rol", back_populates="usuarios")
    ubicacion = relationship("Ubicacion", back_populates="usuarios")
    movimientos_inventario = relationship("MovimientoInventario", back_populates="usuario")
    ventas = relationship("Venta", back_populates="usuario")
    ordenes_compra_compradas = relationship("OrdenCompra", foreign_keys="OrdenCompra.idUsuarioComprador", back_populates="usuario_comprador")
    ordenes_compra_recibidas = relationship("OrdenCompra", foreign_keys="OrdenCompra.idUsuarioReceptor", back_populates="usuario_receptor")
    reposiciones_solicitadas = relationship(
        "SolicitudReposicion",
        foreign_keys="SolicitudReposicion.idUsuarioSolicitante",
        back_populates="usuario_solicitante",
    )
    reposiciones_despachadas = relationship(
        "SolicitudReposicion",
        foreign_keys="SolicitudReposicion.idUsuarioDespachador",
        back_populates="usuario_despachador",
    )
    sesiones = relationship("SesionUsuario", back_populates="usuario")
    reposiciones_recibidas = relationship(
        "SolicitudReposicion",
        foreign_keys="SolicitudReposicion.idUsuarioReceptor",
        back_populates="usuario_receptor",
    )
