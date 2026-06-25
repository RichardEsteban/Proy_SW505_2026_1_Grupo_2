"""Script para crear/resetear el usuario admin en MySQL (Docker).

Uso DENTRO del contenedor del backend:
    docker compose exec backend python init_admin.py

Crea el admin con username='admin' y password='admin123' si no existe,
o lo actualiza si ya existe.
"""
from __future__ import annotations

import os
import sys

# Asegurar que la URL de la BD esté configurada (viene del .env en Docker)
os.environ.setdefault(
    "DATABASE_URL",
    "mysql+pymysql://inventario:inventario@db:3306/inventario",
)

from app.infrastructure.config.settings import get_settings  # noqa: E402

get_settings.cache_clear()

from app.infrastructure.persistence.sqlalchemy.database import SessionLocal  # noqa: E402
from app.infrastructure.persistence.sqlalchemy.models import (  # noqa: E402
    RolModel,
    SucursalModel,
    UsuarioModel,
)
from app.infrastructure.web.services.jwt_service import jwt_service  # noqa: E402

USERNAME = "admin"
PASSWORD = "admin123"

session = SessionLocal()
try:
    rol = session.query(RolModel).filter_by(nombre="Administrador").first()
    if not rol:
        print("✗ No existe el rol 'Administrador'. Corre las migraciones primero.")
        sys.exit(1)

    suc = session.query(SucursalModel).first()
    if not suc:
        print("✗ No existe ninguna sucursal. Corre las migraciones primero.")
        sys.exit(1)

    admin = session.query(UsuarioModel).filter_by(username=USERNAME).first()
    if admin:
        admin.password_hash = jwt_service.hash_password(PASSWORD)
        admin.debe_cambiar_password = False
        admin.estado = "ACTIVO"
        admin.intentos_fallidos = 0
        print(f"✓ Admin actualizado: {USERNAME}")
    else:
        admin = UsuarioModel(
            dni="00000000",
            nombre="Admin",
            apellido="Sistema",
            email="admin@local",
            username=USERNAME,
            password_hash=jwt_service.hash_password(PASSWORD),
            rol_id=rol.id,
            sucursal_id=suc.id,
            estado="ACTIVO",
            debe_cambiar_password=False,
        )
        session.add(admin)
        print(f"✓ Admin creado: {USERNAME}")

    # Bonus: crear vendedor
    rol_vendedor = session.query(RolModel).filter_by(nombre="Vendedor").first()
    if rol_vendedor:
        vend = session.query(UsuarioModel).filter_by(username="vendedor").first()
        if not vend:
            vend = UsuarioModel(
                dni="11111111",
                nombre="Juan",
                apellido="Vendedor",
                email="vendedor@local",
                username="vendedor",
                password_hash=jwt_service.hash_password("vendedor123"),
                rol_id=rol_vendedor.id,
                sucursal_id=suc.id,
                estado="ACTIVO",
                debe_cambiar_password=False,
            )
            session.add(vend)
            print("✓ Vendedor creado: vendedor / vendedor123")

    session.commit()
    print()
    print("=" * 50)
    print(f" Usuarios listos:")
    print(f"   admin     / {PASSWORD}")
    print(f"   vendedor  / vendedor123")
    print("=" * 50)
finally:
    session.close()
