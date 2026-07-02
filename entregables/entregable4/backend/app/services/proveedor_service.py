from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.proveedor import Proveedor
from app.repositories.empresa_repository import EmpresaRepository
from app.repositories.proveedor_repository import ProveedorRepository
from app.schemas.proveedor_schema import (
    ProveedorCreateRequest,
    ProveedorResponse,
    ProveedorUpdateRequest,
)


class ProveedorService:

    @staticmethod
    def _normalizar_identificacion(valor: str) -> str:
        return valor.strip()

    @staticmethod
    def _response(proveedor: Proveedor) -> ProveedorResponse:
        return ProveedorResponse(
            idProveedor=proveedor.idProveedor,
            idEmpresa=proveedor.idEmpresa,
            identificacionFiscal=proveedor.identificacionFiscal,
            razonSocial=proveedor.razonSocial,
            contactoNombre=proveedor.contactoNombre,
            telefono=proveedor.telefono,
            correoElectronico=proveedor.correoElectronico,
            direccion=proveedor.direccion,
            isActivo=proveedor.isActivo,
        )

    @staticmethod
    def listar(db: Session, incluir_inactivos: bool = True) -> list[ProveedorResponse]:
        proveedores = ProveedorRepository.obtener_todos(
            db=db,
            incluir_inactivos=incluir_inactivos,
        )
        return [ProveedorService._response(proveedor) for proveedor in proveedores]

    @staticmethod
    def obtener_por_id(db: Session, id_proveedor: int) -> ProveedorResponse:
        proveedor = ProveedorRepository.obtener_por_id(db, id_proveedor)

        if not proveedor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Proveedor no encontrado",
            )

        return ProveedorService._response(proveedor)

    @staticmethod
    def crear(db: Session, datos: ProveedorCreateRequest) -> ProveedorResponse:
        empresa = EmpresaRepository.obtener_primera(db)

        if not empresa:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Primero debes configurar la empresa",
            )

        identificacion = ProveedorService._normalizar_identificacion(datos.identificacionFiscal)

        existente = ProveedorRepository.obtener_por_identificacion(
            db=db,
            identificacion_fiscal=identificacion,
        )

        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un proveedor con esa identificación fiscal",
            )

        proveedor = Proveedor(
            idEmpresa=empresa.idEmpresa,
            identificacionFiscal=identificacion,
            razonSocial=datos.razonSocial,
            contactoNombre=datos.contactoNombre,
            telefono=datos.telefono,
            correoElectronico=str(datos.correoElectronico) if datos.correoElectronico else None,
            direccion=datos.direccion,
            isActivo=True,
        )

        ProveedorRepository.guardar(db, proveedor)
        db.commit()
        db.refresh(proveedor)

        return ProveedorService._response(proveedor)

    @staticmethod
    def actualizar(
        db: Session,
        id_proveedor: int,
        datos: ProveedorUpdateRequest,
    ) -> ProveedorResponse:
        proveedor = ProveedorRepository.obtener_por_id(db, id_proveedor)

        if not proveedor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Proveedor no encontrado",
            )

        cambios = datos.model_dump(exclude_unset=True)

        if "identificacionFiscal" in cambios:
            cambios["identificacionFiscal"] = ProveedorService._normalizar_identificacion(
                cambios["identificacionFiscal"]
            )
            existente = ProveedorRepository.obtener_por_identificacion(
                db=db,
                identificacion_fiscal=cambios["identificacionFiscal"],
            )
            if existente and existente.idProveedor != id_proveedor:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Ya existe otro proveedor con esa identificación fiscal",
                )

        if "correoElectronico" in cambios and cambios["correoElectronico"] is not None:
            cambios["correoElectronico"] = str(cambios["correoElectronico"])

        for campo, valor in cambios.items():
            setattr(proveedor, campo, valor)

        ProveedorRepository.guardar(db, proveedor)
        db.commit()
        db.refresh(proveedor)

        return ProveedorService._response(proveedor)
