"""Router: administración (usuarios, productos, sucursales, clientes, proveedores)."""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field

from app.domain.use_cases.admin.gestionar_clientes import GestionarClientes
from app.domain.use_cases.admin.gestionar_productos import GestionarProductos
from app.domain.use_cases.admin.gestionar_proveedores import GestionarProveedores
from app.domain.use_cases.admin.gestionar_sucursales import GestionarSucursales
from app.domain.use_cases.admin.gestionar_usuarios import GestionarUsuarios
from app.infrastructure.web.dependencies import (
    get_current_user,
    require_role,
    use_case_gestionar_clientes,
    use_case_gestionar_productos,
    use_case_gestionar_proveedores,
    use_case_gestionar_sucursales,
    use_case_gestionar_usuarios,
)

router = APIRouter(prefix="/admin", tags=["Administración"])


# ---------- Schemas ----------

class CrearUsuarioIn(BaseModel):
    dni: str
    nombre: str
    apellido: str
    email: EmailStr
    username: str
    password: str = Field(min_length=8)
    rol_id: int
    sucursal_id: Optional[int] = None


class ResetPasswordIn(BaseModel):
    password_temporal: str = Field(min_length=8)


class CrearProductoIn(BaseModel):
    sku: str
    codigo_barra: Optional[str] = None
    nombre: str
    descripcion: Optional[str] = None
    categoria_id: Optional[int] = None
    proveedor_id: Optional[int] = None
    precio_compra: float = 0
    precio_venta: float
    unidad_medida: str = "UND"
    incluye_igv: bool = True


class CrearSucursalIn(BaseModel):
    codigo: str
    nombre: str
    direccion: Optional[str] = None
    telefono: Optional[str] = None


class CrearAlmacenIn(BaseModel):
    codigo: str
    nombre: str
    direccion: Optional[str] = None
    responsable_id: Optional[int] = None


class CrearClienteIn(BaseModel):
    tipo_documento: str
    numero_documento: str
    nombre: str
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None


class CrearProveedorIn(BaseModel):
    ruc: str
    razon_social: str
    nombre_comercial: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    contacto_nombre: Optional[str] = None
    contacto_telefono: Optional[str] = None


# ---------- Usuarios ----------

@router.get("/usuarios")
def listar_usuarios(
    sucursal_id: Optional[int] = None,
    uc: GestionarUsuarios = Depends(use_case_gestionar_usuarios),
    _: dict = Depends(require_role("1")),
):
    return [
        {
            "id": u.id,
            "dni": u.dni,
            "username": u.username,
            "nombre_completo": u.nombre_completo,
            "email": u.email,
            "rol_id": u.rol_id,
            "sucursal_id": u.sucursal_id,
            "estado": u.estado.value,
        }
        for u in uc.listar(sucursal_id)
    ]


@router.post("/usuarios", status_code=201)
def crear_usuario(
    datos: CrearUsuarioIn,
    uc: GestionarUsuarios = Depends(use_case_gestionar_usuarios),
    _: dict = Depends(require_role("1")),
):
    try:
        u = uc.crear(**datos.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"id": u.id, "username": u.username}


@router.post("/usuarios/{usuario_id}/reset-password")
def reset_password(
    usuario_id: int,
    datos: ResetPasswordIn,
    uc: GestionarUsuarios = Depends(use_case_gestionar_usuarios),
    _: dict = Depends(require_role("1")),
):
    uc.resetear_password(usuario_id, datos.password_temporal)
    return {"ok": True}


# ---------- Productos ----------

@router.get("/productos")
def listar_productos(
    termino: str = "",
    uc: GestionarProductos = Depends(use_case_gestionar_productos),
    _: dict = Depends(get_current_user),
):
    return [p.__dict__ for p in (uc.buscar(termino) if termino else uc.listar())]


@router.post("/productos", status_code=201)
def crear_producto(
    datos: CrearProductoIn,
    uc: GestionarProductos = Depends(use_case_gestionar_productos),
    _: dict = Depends(require_role("1")),
):
    try:
        p = uc.crear(**datos.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"id": p.id, "sku": p.sku}


# ---------- Sucursales / Almacenes ----------

@router.get("/sucursales")
def listar_sucursales(
    uc: GestionarSucursales = Depends(use_case_gestionar_sucursales),
    _: dict = Depends(get_current_user),
):
    return [{"id": s.id, "codigo": s.codigo, "nombre": s.nombre, "activo": s.activo} for s in uc.listar_sucursales()]


@router.post("/sucursales", status_code=201)
def crear_sucursal(
    datos: CrearSucursalIn,
    uc: GestionarSucursales = Depends(use_case_gestionar_sucursales),
    _: dict = Depends(require_role("1")),
):
    sid = uc.crear_sucursal(**datos.model_dump())
    return {"id": sid}


@router.get("/almacenes")
def listar_almacenes(
    uc: GestionarSucursales = Depends(use_case_gestionar_sucursales),
    _: dict = Depends(get_current_user),
):
    return [{"id": a.id, "codigo": a.codigo, "nombre": a.nombre, "activo": a.activo} for a in uc.listar_almacenes()]


@router.post("/almacenes", status_code=201)
def crear_almacen(
    datos: CrearAlmacenIn,
    uc: GestionarSucursales = Depends(use_case_gestionar_sucursales),
    _: dict = Depends(require_role("1")),
):
    aid = uc.crear_almacen(**datos.model_dump())
    return {"id": aid}


# ---------- Clientes ----------

@router.get("/clientes")
def listar_clientes(
    termino: str = "",
    uc: GestionarClientes = Depends(use_case_gestionar_clientes),
    _: dict = Depends(get_current_user),
):
    return [c.__dict__ for c in uc.listar(termino)]


@router.post("/clientes", status_code=201)
def crear_cliente(
    datos: CrearClienteIn,
    uc: GestionarClientes = Depends(use_case_gestionar_clientes),
    _: dict = Depends(get_current_user),
):
    try:
        c = uc.crear(**datos.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"id": c.id}


# ---------- Proveedores ----------

@router.get("/proveedores")
def listar_proveedores(
    uc: GestionarProveedores = Depends(use_case_gestionar_proveedores),
    _: dict = Depends(get_current_user),
):
    return [p.__dict__ for p in uc.listar()]


@router.post("/proveedores", status_code=201)
def crear_proveedor(
    datos: CrearProveedorIn,
    uc: GestionarProveedores = Depends(use_case_gestionar_proveedores),
    _: dict = Depends(require_role("1")),
):
    try:
        p = uc.crear(**datos.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"id": p.id}
