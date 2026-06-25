"""Caso de uso: Gestión de usuarios (CRUD)."""
from __future__ import annotations

from typing import List, Optional

from app.application.ports.repositorio_usuario import RepositorioUsuario
from app.domain.entities.usuario import EstadoUsuario, Usuario
from app.domain.exceptions.credenciales_invalidas import CredencialesInvalidasError


class GestionarUsuarios:
    def __init__(self, repo: RepositorioUsuario, jwt_service) -> None:
        self._repo = repo
        self._jwt = jwt_service

    def listar(self, sucursal_id: Optional[int] = None) -> List[Usuario]:
        return self._repo.listar(sucursal_id=sucursal_id)

    def crear(
        self,
        dni: str,
        nombre: str,
        apellido: str,
        email: str,
        username: str,
        password: str,
        rol_id: int,
        sucursal_id: Optional[int] = None,
    ) -> Usuario:
        if self._repo.obtener_por_username(username):
            raise CredencialesInvalidasError("Username ya existe")
        if self._repo.obtener_por_dni(dni):
            raise CredencialesInvalidasError("DNI ya registrado")

        usuario = Usuario(
            id=None,
            dni=dni,
            nombre=nombre,
            apellido=apellido,
            email=email,
            username=username,
            password_hash=self._jwt.hash_password(password),
            rol_id=rol_id,
            sucursal_id=sucursal_id,
            estado=EstadoUsuario.ACTIVO,
            debe_cambiar_password=True,
        )
        return self._repo.crear(usuario)

    def actualizar(self, usuario: Usuario) -> Usuario:
        return self._repo.actualizar(usuario)

    def resetear_password(self, usuario_id: int, password_temporal: str) -> None:
        usuario = self._repo.obtener_por_id(usuario_id)
        if usuario is None:
            raise CredencialesInvalidasError("Usuario no existe")
        usuario.password_hash = self._jwt.hash_password(password_temporal)
        usuario.debe_cambiar_password = True
        usuario.intentos_fallidos = 0
        self._repo.actualizar(usuario)

    def desactivar(self, usuario_id: int) -> None:
        usuario = self._repo.obtener_por_id(usuario_id)
        if usuario is None:
            return
        usuario.estado = EstadoUsuario.INACTIVO
        self._repo.actualizar(usuario)
