"""Modelos ORM de SQLAlchemy.

Mapean las entidades de dominio a tablas PostgreSQL. Los nombres de tabla
están en plural y snake_case.
"""
from __future__ import annotations

from datetime import datetime
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.sqlalchemy.database import Base


# ---------- Seguridad ----------

class RolModel(Base):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String(200))
    permisos: Mapped[str] = mapped_column(Text, default="[]")  # JSON string


class SucursalModel(Base):
    __tablename__ = "sucursales"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    direccion: Mapped[str | None] = mapped_column(String(250))
    telefono: Mapped[str | None] = mapped_column(String(20))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)


class AlmacenModel(Base):
    __tablename__ = "almacenes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    direccion: Mapped[str | None] = mapped_column(String(250))
    responsable_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)


class UsuarioModel(Base):
    __tablename__ = "usuarios"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dni: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)
    sucursal_id: Mapped[int | None] = mapped_column(ForeignKey("sucursales.id"))
    estado: Mapped[str] = mapped_column(String(20), default="ACTIVO")
    debe_cambiar_password: Mapped[bool] = mapped_column(Boolean, default=True)
    ultimo_acceso: Mapped[datetime | None] = mapped_column(DateTime)
    intentos_fallidos: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime)


# ---------- Catálogo ----------

class CategoriaModel(Base):
    __tablename__ = "categorias"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    descripcion: Mapped[str | None] = mapped_column(String(200))


class ProveedorModel(Base):
    __tablename__ = "proveedores"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ruc: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    razon_social: Mapped[str] = mapped_column(String(200), nullable=False)
    nombre_comercial: Mapped[str | None] = mapped_column(String(200))
    direccion: Mapped[str | None] = mapped_column(String(250))
    telefono: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(150))
    contacto_nombre: Mapped[str | None] = mapped_column(String(150))
    contacto_telefono: Mapped[str | None] = mapped_column(String(20))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class ProductoModel(Base):
    __tablename__ = "productos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sku: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    codigo_barra: Mapped[str | None] = mapped_column(String(50), unique=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    categoria_id: Mapped[int | None] = mapped_column(ForeignKey("categorias.id"))
    proveedor_id: Mapped[int | None] = mapped_column(ForeignKey("proveedores.id"))
    precio_compra: Mapped[float] = mapped_column(Float, default=0.0)
    precio_venta: Mapped[float] = mapped_column(Float, nullable=False)
    incluye_igv: Mapped[bool] = mapped_column(Boolean, default=True)
    unidad_medida: Mapped[str] = mapped_column(String(10), default="UND")
    imagen_url: Mapped[str | None] = mapped_column(String(500))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class ClienteModel(Base):
    __tablename__ = "clientes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tipo_documento: Mapped[str] = mapped_column(String(10), nullable=False)
    numero_documento: Mapped[str] = mapped_column(String(20), nullable=False)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    direccion: Mapped[str | None] = mapped_column(String(250))
    telefono: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(150))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    __table_args__ = (UniqueConstraint("tipo_documento", "numero_documento"),)


class MetodoPagoModel(Base):
    __tablename__ = "metodos_pago"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String(150))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)


# ---------- Stock ----------

class StockModel(Base):
    __tablename__ = "stock"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    producto_id: Mapped[int] = mapped_column(
        ForeignKey("productos.id"), nullable=False
    )
    ubicacion_tipo: Mapped[str] = mapped_column(String(15), nullable=False)
    ubicacion_id: Mapped[int] = mapped_column(Integer, nullable=False)
    cantidad: Mapped[float] = mapped_column(Float, default=0.0)
    stock_minimo: Mapped[float] = mapped_column(Float, default=0.0)
    stock_maximo: Mapped[float | None] = mapped_column(Float)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    __table_args__ = (
        UniqueConstraint("producto_id", "ubicacion_tipo", "ubicacion_id"),
    )


# ---------- Ventas ----------

class VentaModel(Base):
    __tablename__ = "ventas"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    serie: Mapped[str] = mapped_column(String(10), nullable=False)
    numero: Mapped[str] = mapped_column(String(20), nullable=False)
    tipo_comprobante: Mapped[str] = mapped_column(String(20), nullable=False)
    sucursal_id: Mapped[int] = mapped_column(ForeignKey("sucursales.id"), nullable=False)
    cliente_id: Mapped[int | None] = mapped_column(ForeignKey("clientes.id"))
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    fecha: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    subtotal: Mapped[float] = mapped_column(Float, default=0.0)
    igv: Mapped[float] = mapped_column(Float, default=0.0)
    descuento_total: Mapped[float] = mapped_column(Float, default=0.0)
    total: Mapped[float] = mapped_column(Float, default=0.0)
    estado: Mapped[str] = mapped_column(String(20), default="REGISTRADA")
    pdf_url: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    detalles: Mapped[list["DetalleVentaModel"]] = relationship(
        "DetalleVentaModel", back_populates="venta", cascade="all, delete-orphan"
    )
    __table_args__ = (UniqueConstraint("serie", "numero"),)


class DetalleVentaModel(Base):
    __tablename__ = "detalle_ventas"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    venta_id: Mapped[int] = mapped_column(
        ForeignKey("ventas.id", ondelete="CASCADE"), nullable=False
    )
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"), nullable=False)
    cantidad: Mapped[float] = mapped_column(Float, nullable=False)
    precio_unitario: Mapped[float] = mapped_column(Float, nullable=False)
    descuento: Mapped[float] = mapped_column(Float, default=0.0)
    igv: Mapped[float] = mapped_column(Float, default=0.0)
    subtotal: Mapped[float] = mapped_column(Float, default=0.0)
    total: Mapped[float] = mapped_column(Float, default=0.0)
    venta: Mapped[VentaModel] = relationship("VentaModel", back_populates="detalles")


# ---------- Compras ----------

class CompraModel(Base):
    __tablename__ = "compras"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    proveedor_id: Mapped[int] = mapped_column(
        ForeignKey("proveedores.id"), nullable=False
    )
    almacen_id: Mapped[int] = mapped_column(ForeignKey("almacenes.id"), nullable=False)
    numero_factura: Mapped[str] = mapped_column(String(50), nullable=False)
    subtotal: Mapped[float] = mapped_column(Float, default=0.0)
    igv: Mapped[float] = mapped_column(Float, default=0.0)
    total: Mapped[float] = mapped_column(Float, default=0.0)
    fecha: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)


class DetalleCompraModel(Base):
    __tablename__ = "detalle_compras"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    compra_id: Mapped[int] = mapped_column(
        ForeignKey("compras.id", ondelete="CASCADE"), nullable=False
    )
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"), nullable=False)
    cantidad: Mapped[float] = mapped_column(Float, nullable=False)
    precio_compra: Mapped[float] = mapped_column(Float, nullable=False)
    subtotal: Mapped[float] = mapped_column(Float, default=0.0)


# ---------- Reposición / Solicitudes ----------

class SolicitudModel(Base):
    __tablename__ = "solicitudes_reposicion"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    codigo: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    sucursal_origen_id: Mapped[int] = mapped_column(
        ForeignKey("sucursales.id"), nullable=False
    )
    almacen_destino_id: Mapped[int] = mapped_column(
        ForeignKey("almacenes.id"), nullable=False
    )
    usuario_solicita_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id"), nullable=False
    )
    usuario_evalua_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    estado: Mapped[str] = mapped_column(String(20), default="PENDIENTE")
    motivo: Mapped[str | None] = mapped_column(Text)
    observacion: Mapped[str | None] = mapped_column(Text)
    fecha_solicitud: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    fecha_evaluacion: Mapped[datetime | None] = mapped_column(DateTime)
    fecha_envio: Mapped[datetime | None] = mapped_column(DateTime)
    fecha_recepcion: Mapped[datetime | None] = mapped_column(DateTime)


class DetalleSolicitudModel(Base):
    __tablename__ = "detalle_solicitudes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    solicitud_id: Mapped[int] = mapped_column(
        ForeignKey("solicitudes_reposicion.id", ondelete="CASCADE"), nullable=False
    )
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"), nullable=False)
    cantidad_solicitada: Mapped[float] = mapped_column(Float, nullable=False)
    cantidad_enviada: Mapped[float] = mapped_column(Float, default=0.0)
    cantidad_recibida: Mapped[float] = mapped_column(Float, default=0.0)


# ---------- Alertas ----------

class AlertaModel(Base):
    __tablename__ = "alertas"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"), nullable=False)
    ubicacion_tipo: Mapped[str] = mapped_column(String(15), nullable=False)
    ubicacion_id: Mapped[int] = mapped_column(Integer, nullable=False)
    cantidad_actual: Mapped[float] = mapped_column(Float, default=0.0)
    stock_referencia: Mapped[float] = mapped_column(Float, default=0.0)
    estado: Mapped[str] = mapped_column(String(15), default="ACTIVA")
    mensaje: Mapped[str] = mapped_column(String(1000), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    atendida_at: Mapped[datetime | None] = mapped_column(DateTime)
