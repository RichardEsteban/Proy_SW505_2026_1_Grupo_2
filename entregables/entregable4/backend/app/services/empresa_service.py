from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.empresa_repository import EmpresaRepository
from app.schemas.empresa_schema import EmpresaResponse, EmpresaUpdateRequest


class EmpresaService:

    @staticmethod
    def _response(empresa) -> EmpresaResponse:
        return EmpresaResponse(
            idEmpresa=empresa.idEmpresa,
            nombreEmpresa=empresa.nombreEmpresa,
            isInicializado=empresa.isInicializado,
            timer_revision_minutos=empresa.timer_revision_minutos,
            igv_porcentaje=empresa.igv_porcentaje,
            moneda=empresa.moneda,
        )

    @staticmethod
    def obtener_empresa(db: Session) -> EmpresaResponse:
        empresa = EmpresaRepository.obtener_primera(db)

        if not empresa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe una empresa configurada"
            )

        return EmpresaService._response(empresa)

    @staticmethod
    def actualizar_empresa(db: Session, datos: EmpresaUpdateRequest) -> EmpresaResponse:
        empresa = EmpresaRepository.obtener_primera(db)

        if not empresa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe una empresa configurada"
            )

        cambios = datos.model_dump(exclude_unset=True)

        if "moneda" in cambios and cambios["moneda"]:
            cambios["moneda"] = cambios["moneda"].upper()

        for campo, valor in cambios.items():
            setattr(empresa, campo, valor)

        EmpresaRepository.guardar(db, empresa)
        db.commit()
        db.refresh(empresa)

        return EmpresaService._response(empresa)
