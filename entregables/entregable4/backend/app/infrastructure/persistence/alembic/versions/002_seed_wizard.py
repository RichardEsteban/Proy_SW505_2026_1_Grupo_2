"""Seed del wizard inicial (MySQL): roles, métodos de pago, sucursal, almacén.

Revision ID: 002_seed_wizard
Revises: 001_create_tables
Create Date: 2026-06-18
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002_seed_wizard"
down_revision: Union[str, None] = "001_create_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()

    # Roles
    bind.execute(sa.text(
        "INSERT INTO roles (nombre, descripcion, permisos) VALUES "
        "('Administrador', 'Acceso total al sistema', '[\"*\"]'),"
        "('Almacenero', 'Gestiona entradas y transferencias', '[\"almacen:*\"]'),"
        "('Vendedor', 'Opera el POS', '[\"ventas:create\",\"inventario:read\"]'),"
        "('Supervisor', 'Aprueba solicitudes y ve reportes', '[\"reposicion:*\",\"reportes:read\"]')"
    ))

    # Métodos de pago
    bind.execute(sa.text(
        "INSERT INTO metodos_pago (nombre, descripcion) VALUES "
        "('Efectivo', 'Pago en efectivo'),"
        "('Tarjeta', 'Pago con tarjeta débito/crédito'),"
        "('Yape/Plin', 'Transferencia inmediata'),"
        "('Transferencia', 'Transferencia bancaria')"
    ))

    # Sucursal y almacén iniciales
    bind.execute(sa.text(
        "INSERT INTO sucursales (codigo, nombre, direccion) VALUES "
        "('S001', 'Sucursal Principal', 'Por definir')"
    ))
    bind.execute(sa.text(
        "INSERT INTO almacenes (codigo, nombre, direccion) VALUES "
        "('A001', 'Almacén Central', 'Por definir')"
    ))


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(sa.text("DELETE FROM almacenes WHERE codigo='A001'"))
    bind.execute(sa.text("DELETE FROM sucursales WHERE codigo='S001'"))
    bind.execute(sa.text("DELETE FROM metodos_pago WHERE nombre IN ('Efectivo','Tarjeta','Yape/Plin','Transferencia')"))
    bind.execute(sa.text("DELETE FROM roles WHERE nombre IN ('Administrador','Almacenero','Vendedor','Supervisor')"))
