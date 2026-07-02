from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.constants import Roles
from app.core.dependencias import get_current_user
from app.core.permissions import require_roles
from app.db.session import get_db
from app.schemas.cliente_schema import ClienteCreateRequest, ClienteResponse, ClienteUpdateRequest
from app.services.cliente_service import ClienteService


router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"]
)


@router.get("", response_model=list[ClienteResponse])
def listar_clientes(
    incluir_inactivos: bool = Query(default=False),
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    if usuario_actual.rol.nombreRol not in (Roles.ADMIN, Roles.SUPERVISOR_ALMACEN):
        incluir_inactivos = False
    return ClienteService.listar(db=db, incluir_inactivos=incluir_inactivos)


@router.get("/{id_cliente}", response_model=ClienteResponse)
def obtener_cliente(
    id_cliente: int,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    return ClienteService.obtener_por_id(db=db, id_cliente=id_cliente)


@router.post(
    "",
    response_model=ClienteResponse,
    dependencies=[Depends(require_roles(Roles.ADMIN, Roles.VENDEDOR, Roles.SUPERVISOR_SUCURSAL))]
)
def crear_cliente(
    datos: ClienteCreateRequest,
    db: Session = Depends(get_db),
):
    return ClienteService.crear(db=db, datos=datos)


@router.patch(
    "/{id_cliente}",
    response_model=ClienteResponse,
    dependencies=[Depends(require_roles(Roles.ADMIN, Roles.VENDEDOR, Roles.SUPERVISOR_SUCURSAL))]
)
def actualizar_cliente(
    id_cliente: int,
    datos: ClienteUpdateRequest,
    db: Session = Depends(get_db),
):
    return ClienteService.actualizar(db=db, id_cliente=id_cliente, datos=datos)
