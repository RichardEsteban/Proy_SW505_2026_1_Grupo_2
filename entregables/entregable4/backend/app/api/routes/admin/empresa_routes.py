from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.constants import Roles
from app.core.permissions import require_roles
from app.db.session import get_db
from app.schemas.empresa_schema import EmpresaResponse, EmpresaUpdateRequest
from app.services.empresa_service import EmpresaService


router = APIRouter(
    prefix="/empresa",
    tags=["Empresa"]
)


@router.get(
    "",
    response_model=EmpresaResponse,
    dependencies=[Depends(require_roles(Roles.ADMIN, Roles.SUPERVISOR_ALMACEN))]
)
def obtener_empresa(db: Session = Depends(get_db)):
    return EmpresaService.obtener_empresa(db)


@router.put(
    "",
    response_model=EmpresaResponse,
    dependencies=[Depends(require_roles(Roles.ADMIN))]
)
def actualizar_empresa(
    datos: EmpresaUpdateRequest,
    db: Session = Depends(get_db)
):
    return EmpresaService.actualizar_empresa(db=db, datos=datos)
