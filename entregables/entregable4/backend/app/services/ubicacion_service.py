from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.ubicacion import Ubicacion
from app.repositories.empresa_repository import EmpresaRepository
from app.repositories.ubicacion_repository import UbicacionRepository
from app.schemas.ubicacion_schema import (
    UbicacionCreateRequest,
    UbicacionResponse,
    UbicacionUpdateRequest,
)


class UbicacionService:

    @staticmethod
    def _response(ubicacion: Ubicacion) -> UbicacionResponse:
        return UbicacionResponse(
            idUbicacion=ubicacion.idUbicacion,
            idEmpresa=ubicacion.idEmpresa,
            nombreUbicacion=ubicacion.nombreUbicacion,
            tipoUbicacion=ubicacion.tipoUbicacion,
            direccion=ubicacion.direccion,
            isActivo=ubicacion.isActivo,
        )

    @staticmethod
    def listar(db: Session, incluir_inactivas: bool = True) -> list[UbicacionResponse]:
        ubicaciones = UbicacionRepository.obtener_todas(
            db=db,
            incluir_inactivas=incluir_inactivas
        )
        return [UbicacionService._response(ubicacion) for ubicacion in ubicaciones]

    @staticmethod
    def obtener_por_id(db: Session, id_ubicacion: int) -> UbicacionResponse:
        ubicacion = UbicacionRepository.obtener_por_id(db, id_ubicacion)

        if not ubicacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ubicación no encontrada"
            )

        return UbicacionService._response(ubicacion)

    @staticmethod
    def crear(db: Session, datos: UbicacionCreateRequest) -> UbicacionResponse:
        empresa = EmpresaRepository.obtener_primera(db)

        if not empresa:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Primero debes configurar la empresa"
            )

        existente = UbicacionRepository.obtener_por_nombre(db, datos.nombreUbicacion)

        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una ubicación con ese nombre"
            )

        ubicacion = Ubicacion(
            idEmpresa=empresa.idEmpresa,
            nombreUbicacion=datos.nombreUbicacion,
            tipoUbicacion=datos.tipoUbicacion,
            direccion=datos.direccion,
            isActivo=True,
        )

        UbicacionRepository.guardar(db, ubicacion)
        db.commit()
        db.refresh(ubicacion)

        return UbicacionService._response(ubicacion)

    @staticmethod
    def actualizar(
        db: Session,
        id_ubicacion: int,
        datos: UbicacionUpdateRequest
    ) -> UbicacionResponse:
        ubicacion = UbicacionRepository.obtener_por_id(db, id_ubicacion)

        if not ubicacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ubicación no encontrada"
            )

        cambios = datos.model_dump(exclude_unset=True)

        if "nombreUbicacion" in cambios:
            existente = UbicacionRepository.obtener_por_nombre(db, cambios["nombreUbicacion"])
            if existente and existente.idUbicacion != id_ubicacion:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Ya existe otra ubicación con ese nombre"
                )

        for campo, valor in cambios.items():
            setattr(ubicacion, campo, valor)

        UbicacionRepository.guardar(db, ubicacion)
        db.commit()
        db.refresh(ubicacion)

        return UbicacionService._response(ubicacion)
