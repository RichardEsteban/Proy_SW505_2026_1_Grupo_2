"""Router: reposición (solicitudes)."""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.domain.entities.solicitud import EstadoSolicitud
from app.domain.use_cases.reposicion.confirmar_recepcion import ConfirmarRecepcion
from app.domain.use_cases.reposicion.evaluar_solicitud import EvaluarSolicitud
from app.domain.use_cases.reposicion.generar_solicitud import (
    GenerarSolicitud,
    ItemSolicitudInput,
    SolicitudInput,
)
from app.domain.use_cases.reposicion.registrar_envio import RegistrarEnvio
from app.infrastructure.persistence.sqlalchemy.repositories import (
    SqlAlchemySolicitudRepository,
)
from app.infrastructure.web.dependencies import (
    get_current_user,
    get_db,
    use_case_confirmar_recepcion,
    use_case_evaluar_solicitud,
    use_case_generar_solicitud,
    use_case_registrar_envio,
)
from sqlalchemy.orm import Session

router = APIRouter(prefix="/reposicion", tags=["Reposición"])


class ItemSolicitudSchema(BaseModel):
    producto_id: int
    cantidad: float


class GenerarSolicitudIn(BaseModel):
    sucursal_origen_id: int
    almacen_destino_id: int
    motivo: Optional[str] = None
    items: List[ItemSolicitudSchema]


class EvaluarIn(BaseModel):
    accion: str  # "aprobar" | "rechazar"
    motivo: Optional[str] = None


@router.post("/solicitudes", status_code=201)
def generar(
    datos: GenerarSolicitudIn,
    uc: GenerarSolicitud = Depends(use_case_generar_solicitud),
    user: dict = Depends(get_current_user),
) -> dict:
    sol = uc.ejecutar(
        SolicitudInput(
            sucursal_origen_id=datos.sucursal_origen_id,
            almacen_destino_id=datos.almacen_destino_id,
            usuario_solicita_id=int(user["sub"]),
            motivo=datos.motivo,
            items=[ItemSolicitudInput(**i.model_dump()) for i in datos.items],
        )
    )
    return {
        "id": sol.id,
        "codigo": sol.codigo,
        "estado": sol.estado.value,
        "fecha_solicitud": sol.fecha_solicitud.isoformat(),
    }


@router.get("/solicitudes")
def listar(
    sucursal_id: Optional[int] = None,
    estado: Optional[EstadoSolicitud] = None,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
) -> list:
    repo = SqlAlchemySolicitudRepository(db)
    return [
        {
            "id": s.id,
            "codigo": s.codigo,
            "estado": s.estado.value,
            "sucursal_origen_id": s.sucursal_origen_id,
            "almacen_destino_id": s.almacen_destino_id,
            "fecha_solicitud": s.fecha_solicitud.isoformat() if s.fecha_solicitud else None,
        }
        for s in repo.listar(sucursal_id, estado)
    ]


@router.post("/solicitudes/{solicitud_id}/evaluar")
def evaluar(
    solicitud_id: int,
    datos: EvaluarIn,
    uc: EvaluarSolicitud = Depends(use_case_evaluar_solicitud),
    user: dict = Depends(get_current_user),
) -> dict:
    try:
        if datos.accion == "aprobar":
            uc.aprobar(solicitud_id, int(user["sub"]))
        elif datos.accion == "rechazar":
            uc.rechazar(solicitud_id, int(user["sub"]), datos.motivo or "Sin motivo")
        else:
            raise HTTPException(status_code=400, detail="Acción inválida")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True}


@router.post("/solicitudes/{solicitud_id}/enviar")
def enviar(
    solicitud_id: int,
    uc: RegistrarEnvio = Depends(use_case_registrar_envio),
    user: dict = Depends(get_current_user),
) -> dict:
    try:
        uc.ejecutar(solicitud_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True}


@router.post("/solicitudes/{solicitud_id}/recibir")
def recibir(
    solicitud_id: int,
    uc: ConfirmarRecepcion = Depends(use_case_confirmar_recepcion),
    user: dict = Depends(get_current_user),
) -> dict:
    try:
        uc.ejecutar(solicitud_id, int(user["sub"]))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True}
