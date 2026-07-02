from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.constants import Roles
from app.core.permissions import require_roles
from app.db.session import get_db
from app.schemas.reposicion_schema import (
    EstadoSolicitudReposicion,
    SolicitudReposicionCreateRequest,
    SolicitudReposicionGestionRequest,
    SolicitudReposicionResponse,
)
from app.services.reposicion_service import ReposicionService


router = APIRouter(
    prefix="/reposiciones",
    tags=["Reposiciones"]
)


@router.get(
    "",
    response_model=list[SolicitudReposicionResponse],
    dependencies=[Depends(require_roles(Roles.ADMIN, Roles.SUPERVISOR_ALMACEN, Roles.SUPERVISOR_SUCURSAL))]
)
def listar_reposiciones(
    id_ubicacion_origen: int | None = Query(default=None),
    id_ubicacion_destino: int | None = Query(default=None),
    estado: EstadoSolicitudReposicion | None = Query(default=None),
    desde: datetime | None = Query(default=None),
    hasta: datetime | None = Query(default=None),
    limite: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    usuario_actual=Depends(require_roles(Roles.ADMIN, Roles.SUPERVISOR_ALMACEN, Roles.SUPERVISOR_SUCURSAL)),
):
    return ReposicionService.listar(
        db=db,
        usuario_actual=usuario_actual,
        id_ubicacion_origen=id_ubicacion_origen,
        id_ubicacion_destino=id_ubicacion_destino,
        estado=estado,
        desde=desde,
        hasta=hasta,
        limite=limite,
    )


@router.post(
    "",
    response_model=SolicitudReposicionResponse,
    dependencies=[Depends(require_roles(Roles.ADMIN, Roles.SUPERVISOR_ALMACEN, Roles.SUPERVISOR_SUCURSAL))]
)
def crear_reposicion(
    datos: SolicitudReposicionCreateRequest,
    db: Session = Depends(get_db),
    usuario_actual=Depends(require_roles(Roles.ADMIN, Roles.SUPERVISOR_ALMACEN, Roles.SUPERVISOR_SUCURSAL)),
):
    return ReposicionService.crear(db=db, datos=datos, usuario_actual=usuario_actual)



@router.patch(
    "/{id_solicitud_reposicion}/editar",
    response_model=SolicitudReposicionResponse,
    dependencies=[Depends(require_roles(Roles.ADMIN, Roles.SUPERVISOR_ALMACEN, Roles.SUPERVISOR_SUCURSAL))]
)
def editar_reposicion(
    id_solicitud_reposicion: int,
    datos: SolicitudReposicionCreateRequest,
    db: Session = Depends(get_db),
    usuario_actual=Depends(require_roles(Roles.ADMIN, Roles.SUPERVISOR_ALMACEN, Roles.SUPERVISOR_SUCURSAL)),
):
    return ReposicionService.editar(
        db=db,
        id_solicitud_reposicion=id_solicitud_reposicion,
        datos=datos,
        usuario_actual=usuario_actual,
    )


@router.get(
    "/{id_solicitud_reposicion}",
    response_model=SolicitudReposicionResponse,
    dependencies=[Depends(require_roles(Roles.ADMIN, Roles.SUPERVISOR_ALMACEN, Roles.SUPERVISOR_SUCURSAL))]
)
def obtener_reposicion(
    id_solicitud_reposicion: int,
    db: Session = Depends(get_db),
    usuario_actual=Depends(require_roles(Roles.ADMIN, Roles.SUPERVISOR_ALMACEN, Roles.SUPERVISOR_SUCURSAL)),
):
    return ReposicionService.obtener_por_id(
        db=db,
        id_solicitud_reposicion=id_solicitud_reposicion,
        usuario_actual=usuario_actual,
    )


@router.patch(
    "/{id_solicitud_reposicion}/abrir-revision",
    response_model=SolicitudReposicionResponse,
    dependencies=[Depends(require_roles(Roles.ADMIN, Roles.SUPERVISOR_ALMACEN))]
)
def abrir_revision_reposicion(
    id_solicitud_reposicion: int,
    datos: SolicitudReposicionGestionRequest | None = None,
    db: Session = Depends(get_db),
    usuario_actual=Depends(require_roles(Roles.ADMIN, Roles.SUPERVISOR_ALMACEN)),
):
    return ReposicionService.abrir_revision(
        db=db,
        id_solicitud_reposicion=id_solicitud_reposicion,
        datos=datos or SolicitudReposicionGestionRequest(),
        usuario_actual=usuario_actual,
    )


@router.patch(
    "/{id_solicitud_reposicion}/aprobar",
    response_model=SolicitudReposicionResponse,
    dependencies=[Depends(require_roles(Roles.ADMIN, Roles.SUPERVISOR_ALMACEN))]
)
def aprobar_reposicion(
    id_solicitud_reposicion: int,
    datos: SolicitudReposicionGestionRequest | None = None,
    db: Session = Depends(get_db),
    usuario_actual=Depends(require_roles(Roles.ADMIN, Roles.SUPERVISOR_ALMACEN)),
):
    return ReposicionService.aprobar(
        db=db,
        id_solicitud_reposicion=id_solicitud_reposicion,
        datos=datos or SolicitudReposicionGestionRequest(),
        usuario_actual=usuario_actual,
    )


@router.patch(
    "/{id_solicitud_reposicion}/rechazar",
    response_model=SolicitudReposicionResponse,
    dependencies=[Depends(require_roles(Roles.ADMIN, Roles.SUPERVISOR_ALMACEN))]
)
def rechazar_reposicion(
    id_solicitud_reposicion: int,
    datos: SolicitudReposicionGestionRequest | None = None,
    db: Session = Depends(get_db),
    usuario_actual=Depends(require_roles(Roles.ADMIN, Roles.SUPERVISOR_ALMACEN)),
):
    return ReposicionService.rechazar(
        db=db,
        id_solicitud_reposicion=id_solicitud_reposicion,
        datos=datos or SolicitudReposicionGestionRequest(),
        usuario_actual=usuario_actual,
    )


@router.patch(
    "/{id_solicitud_reposicion}/enviar",
    response_model=SolicitudReposicionResponse,
    dependencies=[Depends(require_roles(Roles.ADMIN, Roles.SUPERVISOR_ALMACEN))]
)
def enviar_reposicion(
    id_solicitud_reposicion: int,
    datos: SolicitudReposicionGestionRequest | None = None,
    db: Session = Depends(get_db),
    usuario_actual=Depends(require_roles(Roles.ADMIN, Roles.SUPERVISOR_ALMACEN)),
):
    return ReposicionService.enviar(
        db=db,
        id_solicitud_reposicion=id_solicitud_reposicion,
        datos=datos or SolicitudReposicionGestionRequest(),
        usuario_actual=usuario_actual,
    )


@router.patch(
    "/{id_solicitud_reposicion}/recibir",
    response_model=SolicitudReposicionResponse,
    dependencies=[Depends(require_roles(Roles.ADMIN, Roles.SUPERVISOR_ALMACEN, Roles.SUPERVISOR_SUCURSAL))]
)
def recibir_reposicion(
    id_solicitud_reposicion: int,
    datos: SolicitudReposicionGestionRequest | None = None,
    db: Session = Depends(get_db),
    usuario_actual=Depends(require_roles(Roles.ADMIN, Roles.SUPERVISOR_ALMACEN, Roles.SUPERVISOR_SUCURSAL)),
):
    return ReposicionService.recibir(
        db=db,
        id_solicitud_reposicion=id_solicitud_reposicion,
        datos=datos or SolicitudReposicionGestionRequest(),
        usuario_actual=usuario_actual,
    )


@router.patch(
    "/{id_solicitud_reposicion}/cancelar",
    response_model=SolicitudReposicionResponse,
    dependencies=[Depends(require_roles(Roles.ADMIN, Roles.SUPERVISOR_ALMACEN, Roles.SUPERVISOR_SUCURSAL))]
)
def cancelar_reposicion(
    id_solicitud_reposicion: int,
    datos: SolicitudReposicionGestionRequest | None = None,
    db: Session = Depends(get_db),
    usuario_actual=Depends(require_roles(Roles.ADMIN, Roles.SUPERVISOR_ALMACEN, Roles.SUPERVISOR_SUCURSAL)),
):
    return ReposicionService.cancelar(
        db=db,
        id_solicitud_reposicion=id_solicitud_reposicion,
        datos=datos or SolicitudReposicionGestionRequest(),
        usuario_actual=usuario_actual,
    )


@router.patch(
    "/{id_solicitud_reposicion}/anular",
    response_model=SolicitudReposicionResponse,
    dependencies=[Depends(require_roles(Roles.ADMIN, Roles.SUPERVISOR_ALMACEN, Roles.SUPERVISOR_SUCURSAL))]
)
def anular_reposicion(
    id_solicitud_reposicion: int,
    datos: SolicitudReposicionGestionRequest | None = None,
    db: Session = Depends(get_db),
    usuario_actual=Depends(require_roles(Roles.ADMIN, Roles.SUPERVISOR_ALMACEN, Roles.SUPERVISOR_SUCURSAL)),
):
    return ReposicionService.anular(
        db=db,
        id_solicitud_reposicion=id_solicitud_reposicion,
        datos=datos or SolicitudReposicionGestionRequest(),
        usuario_actual=usuario_actual,
    )
