from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.constants import Roles
from app.core.dependencias import get_current_user
from app.db.session import get_db
from app.schemas.metodo_pago_schema import MetodoPagoResponse
from app.services.metodo_pago_service import MetodoPagoService


router = APIRouter(
    prefix="/metodos-pago",
    tags=["Métodos de pago"]
)


@router.get("", response_model=list[MetodoPagoResponse])
def listar_metodos_pago(
    incluir_inactivos: bool = Query(default=False),
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    if usuario_actual.rol.nombreRol not in (Roles.ADMIN, Roles.SUPERVISOR_ALMACEN):
        incluir_inactivos = False
    return MetodoPagoService.listar(db=db, incluir_inactivos=incluir_inactivos)
