from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencias import get_current_user
from app.db.session import get_db
from app.schemas.alerta_schema import AlertaStockResponse
from app.services.alerta_service import AlertaService


router = APIRouter(
    prefix="/alertas",
    tags=["Alertas de stock"]
)


@router.get("", response_model=list[AlertaStockResponse])
def listar_alertas(
    id_ubicacion: int | None = Query(default=None),
    estado: str | None = Query(default="PENDIENTE"),
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    return AlertaService.listar(
        db=db,
        usuario_actual=usuario_actual,
        id_ubicacion=id_ubicacion,
        estado=estado,
    )


@router.patch("/{id_alerta}/leer", response_model=AlertaStockResponse)
def marcar_alerta_como_leida(
    id_alerta: int,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    return AlertaService.marcar_como_leida(
        db=db,
        id_alerta=id_alerta,
        usuario_actual=usuario_actual,
    )
