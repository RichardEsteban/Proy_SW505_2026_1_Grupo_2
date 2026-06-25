"""Caso de uso: Inicializar sistema (wizard de primer arranque).

Crea datos mínimos: rol Administrador, sucursal principal, almacén central,
usuario administrador, IGV, etc.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from app.application.ports.repositorio_usuario import RepositorioUsuario


@dataclass
class DatosInicializacion:
    admin_dni: str
    admin_nombre: str
    admin_apellido: str
    admin_email: str
    admin_username: str
    admin_password: str
    empresa_nombre: str
    empresa_ruc: str
    igv_porcentaje: float
    moneda: str
    sucursal_nombre: str
    almacen_nombre: str


class InicializarSistema:
    def __init__(self, uow_factory, jwt_service) -> None:
        self._uow_factory = uow_factory
        self._jwt = jwt_service

    def ejecutar(self, datos: DatosInicializacion) -> Dict[str, Any]:
        """Ejecuta el wizard inicial. Idempotente: si ya hay admin, no hace nada."""
        with self._uow_factory() as uow:
            # Verificar si ya fue inicializado
            usuarios = uow.repos_usuarios.listar()
            if any(u.rol_id == 1 for u in usuarios):
                return {"inicializado": True, "motivo": "Ya existe un administrador"}

            # 1) Rol admin
            rol_admin_id = uow.repos_roles.crear(
                nombre="Administrador", descripcion="Acceso total", permisos=["*"]
            )

            # 2) Sucursal principal
            suc_id = uow.repos_sucursales.crear(
                codigo="S001", nombre=datos.sucursal_nombre, direccion="Principal"
            )

            # 3) Almacén central
            alm_id = uow.repos_almacenes.crear(
                codigo="A001", nombre=datos.almacen_nombre, direccion="Central"
            )

            # 4) Usuario admin
            from app.domain.entities.usuario import EstadoUsuario, Usuario

            admin = Usuario(
                id=None,
                dni=datos.admin_dni,
                nombre=datos.admin_nombre,
                apellido=datos.admin_apellido,
                email=datos.admin_email,
                username=datos.admin_username,
                password_hash=self._jwt.hash_password(datos.admin_password),
                rol_id=rol_admin_id,
                sucursal_id=suc_id,
                estado=EstadoUsuario.ACTIVO,
                debe_cambiar_password=False,
            )
            usuario = uow.repos_usuarios.crear(admin)
            uow.commit()

            return {
                "inicializado": True,
                "admin_id": usuario.id,
                "sucursal_id": suc_id,
                "almacen_id": alm_id,
            }
