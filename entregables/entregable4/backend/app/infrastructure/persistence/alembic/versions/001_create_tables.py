"""Creación inicial de todas las tablas del sistema (MySQL).

Revision ID: 001_create_tables
Revises:
Create Date: 2026-06-18
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001_create_tables"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Seguridad / catálogos base ---
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("nombre", sa.String(50), nullable=False, unique=True),
        sa.Column("descripcion", sa.String(200)),
        sa.Column("permisos", sa.String(1000), server_default="[]"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_table(
        "sucursales",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("codigo", sa.String(20), nullable=False, unique=True),
        sa.Column("nombre", sa.String(150), nullable=False),
        sa.Column("direccion", sa.String(250)),
        sa.Column("telefono", sa.String(20)),
        sa.Column("activo", sa.Boolean, server_default=sa.text("1")),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_table(
        "almacenes",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("codigo", sa.String(20), nullable=False, unique=True),
        sa.Column("nombre", sa.String(150), nullable=False),
        sa.Column("direccion", sa.String(250)),
        sa.Column("responsable_id", sa.Integer),
        sa.Column("activo", sa.Boolean, server_default=sa.text("1")),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("dni", sa.String(15), nullable=False, unique=True),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("apellido", sa.String(100), nullable=False),
        sa.Column("email", sa.String(150), nullable=False, unique=True),
        sa.Column("username", sa.String(50), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("rol_id", sa.Integer, sa.ForeignKey("roles.id"), nullable=False),
        sa.Column("sucursal_id", sa.Integer, sa.ForeignKey("sucursales.id")),
        sa.Column("estado", sa.String(20), server_default="ACTIVO"),
        sa.Column("debe_cambiar_password", sa.Boolean, server_default=sa.text("1")),
        sa.Column("ultimo_acceso", sa.DateTime),
        sa.Column("intentos_fallidos", sa.Integer, server_default="0"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_table(
        "categorias",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("nombre", sa.String(100), nullable=False, unique=True),
        sa.Column("descripcion", sa.String(200)),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_table(
        "proveedores",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("ruc", sa.String(20), nullable=False, unique=True),
        sa.Column("razon_social", sa.String(200), nullable=False),
        sa.Column("nombre_comercial", sa.String(200)),
        sa.Column("direccion", sa.String(250)),
        sa.Column("telefono", sa.String(20)),
        sa.Column("email", sa.String(150)),
        sa.Column("contacto_nombre", sa.String(150)),
        sa.Column("contacto_telefono", sa.String(20)),
        sa.Column("activo", sa.Boolean, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_table(
        "productos",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("sku", sa.String(50), nullable=False, unique=True),
        sa.Column("codigo_barra", sa.String(50), unique=True),
        sa.Column("nombre", sa.String(200), nullable=False),
        sa.Column("descripcion", sa.Text),
        sa.Column("categoria_id", sa.Integer, sa.ForeignKey("categorias.id")),
        sa.Column("proveedor_id", sa.Integer, sa.ForeignKey("proveedores.id")),
        sa.Column("precio_compra", sa.Float, server_default="0"),
        sa.Column("precio_venta", sa.Float, nullable=False),
        sa.Column("incluye_igv", sa.Boolean, server_default=sa.text("1")),
        sa.Column("unidad_medida", sa.String(10), server_default="UND"),
        sa.Column("imagen_url", sa.String(500)),
        sa.Column("activo", sa.Boolean, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_table(
        "clientes",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("tipo_documento", sa.String(10), nullable=False),
        sa.Column("numero_documento", sa.String(20), nullable=False),
        sa.Column("nombre", sa.String(200), nullable=False),
        sa.Column("direccion", sa.String(250)),
        sa.Column("telefono", sa.String(20)),
        sa.Column("email", sa.String(150)),
        sa.Column("activo", sa.Boolean, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
        sa.UniqueConstraint("tipo_documento", "numero_documento"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_table(
        "metodos_pago",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("nombre", sa.String(50), nullable=False, unique=True),
        sa.Column("descripcion", sa.String(150)),
        sa.Column("activo", sa.Boolean, server_default=sa.text("1")),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_table(
        "stock",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("producto_id", sa.Integer, sa.ForeignKey("productos.id"), nullable=False),
        sa.Column("ubicacion_tipo", sa.String(15), nullable=False),
        sa.Column("ubicacion_id", sa.Integer, nullable=False),
        sa.Column("cantidad", sa.Float, server_default="0"),
        sa.Column("stock_minimo", sa.Float, server_default="0"),
        sa.Column("stock_maximo", sa.Float),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
        sa.UniqueConstraint("producto_id", "ubicacion_tipo", "ubicacion_id"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_table(
        "ventas",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("serie", sa.String(10), nullable=False),
        sa.Column("numero", sa.String(20), nullable=False),
        sa.Column("tipo_comprobante", sa.String(20), nullable=False),
        sa.Column("sucursal_id", sa.Integer, sa.ForeignKey("sucursales.id"), nullable=False),
        sa.Column("cliente_id", sa.Integer, sa.ForeignKey("clientes.id")),
        sa.Column("usuario_id", sa.Integer, sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("fecha", sa.DateTime, server_default=sa.func.now()),
        sa.Column("subtotal", sa.Float, server_default="0"),
        sa.Column("igv", sa.Float, server_default="0"),
        sa.Column("descuento_total", sa.Float, server_default="0"),
        sa.Column("total", sa.Float, server_default="0"),
        sa.Column("estado", sa.String(20), server_default="REGISTRADA"),
        sa.Column("pdf_url", sa.String(500)),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.UniqueConstraint("serie", "numero"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_table(
        "detalle_ventas",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("venta_id", sa.Integer, sa.ForeignKey("ventas.id", ondelete="CASCADE"), nullable=False),
        sa.Column("producto_id", sa.Integer, sa.ForeignKey("productos.id"), nullable=False),
        sa.Column("cantidad", sa.Float, nullable=False),
        sa.Column("precio_unitario", sa.Float, nullable=False),
        sa.Column("descuento", sa.Float, server_default="0"),
        sa.Column("igv", sa.Float, server_default="0"),
        sa.Column("subtotal", sa.Float, server_default="0"),
        sa.Column("total", sa.Float, server_default="0"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_table(
        "compras",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("proveedor_id", sa.Integer, sa.ForeignKey("proveedores.id"), nullable=False),
        sa.Column("almacen_id", sa.Integer, sa.ForeignKey("almacenes.id"), nullable=False),
        sa.Column("numero_factura", sa.String(50), nullable=False),
        sa.Column("subtotal", sa.Float, server_default="0"),
        sa.Column("igv", sa.Float, server_default="0"),
        sa.Column("total", sa.Float, server_default="0"),
        sa.Column("fecha", sa.DateTime, server_default=sa.func.now()),
        sa.Column("usuario_id", sa.Integer, sa.ForeignKey("usuarios.id"), nullable=False),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_table(
        "detalle_compras",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("compra_id", sa.Integer, sa.ForeignKey("compras.id", ondelete="CASCADE"), nullable=False),
        sa.Column("producto_id", sa.Integer, sa.ForeignKey("productos.id"), nullable=False),
        sa.Column("cantidad", sa.Float, nullable=False),
        sa.Column("precio_compra", sa.Float, nullable=False),
        sa.Column("subtotal", sa.Float, server_default="0"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_table(
        "solicitudes_reposicion",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("codigo", sa.String(30), nullable=False, unique=True),
        sa.Column("sucursal_origen_id", sa.Integer, sa.ForeignKey("sucursales.id"), nullable=False),
        sa.Column("almacen_destino_id", sa.Integer, sa.ForeignKey("almacenes.id"), nullable=False),
        sa.Column("usuario_solicita_id", sa.Integer, sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("usuario_evalua_id", sa.Integer, sa.ForeignKey("usuarios.id")),
        sa.Column("estado", sa.String(20), server_default="PENDIENTE"),
        sa.Column("motivo", sa.Text),
        sa.Column("observacion", sa.Text),
        sa.Column("fecha_solicitud", sa.DateTime, server_default=sa.func.now()),
        sa.Column("fecha_evaluacion", sa.DateTime),
        sa.Column("fecha_envio", sa.DateTime),
        sa.Column("fecha_recepcion", sa.DateTime),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_table(
        "detalle_solicitudes",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("solicitud_id", sa.Integer, sa.ForeignKey("solicitudes_reposicion.id", ondelete="CASCADE"), nullable=False),
        sa.Column("producto_id", sa.Integer, sa.ForeignKey("productos.id"), nullable=False),
        sa.Column("cantidad_solicitada", sa.Float, nullable=False),
        sa.Column("cantidad_enviada", sa.Float, server_default="0"),
        sa.Column("cantidad_recibida", sa.Float, server_default="0"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_table(
        "alertas",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("tipo", sa.String(20), nullable=False),
        sa.Column("producto_id", sa.Integer, sa.ForeignKey("productos.id"), nullable=False),
        sa.Column("ubicacion_tipo", sa.String(15), nullable=False),
        sa.Column("ubicacion_id", sa.Integer, nullable=False),
        sa.Column("cantidad_actual", sa.Float, server_default="0"),
        sa.Column("stock_referencia", sa.Float, server_default="0"),
        sa.Column("estado", sa.String(15), server_default="ACTIVA"),
        sa.Column("mensaje", sa.String(1000), server_default=""),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("atendida_at", sa.DateTime),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )

    # Índices
    op.create_index("idx_stock_producto", "stock", ["producto_id"])
    op.create_index("idx_stock_ubicacion", "stock", ["ubicacion_tipo", "ubicacion_id"])
    op.create_index("idx_ventas_fecha", "ventas", ["fecha"])
    op.create_index("idx_ventas_sucursal", "ventas", ["sucursal_id"])
    op.create_index("idx_alertas_estado", "alertas", ["estado"])


def downgrade() -> None:
    for tbl in [
        "alertas", "detalle_solicitudes", "solicitudes_reposicion",
        "detalle_compras", "compras", "detalle_ventas", "ventas",
        "stock", "metodos_pago", "clientes", "productos", "proveedores",
        "categorias", "usuarios", "almacenes", "sucursales", "roles",
    ]:
        op.drop_table(tbl)
