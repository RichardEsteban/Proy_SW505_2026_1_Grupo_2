from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.categoria import Categoria
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.empresa_repository import EmpresaRepository
from app.schemas.categoria_schema import (
    CategoriaCreateRequest,
    CategoriaResponse,
    CategoriaUpdateRequest,
)


class CategoriaService:

    @staticmethod
    def _response(categoria: Categoria) -> CategoriaResponse:
        return CategoriaResponse(
            idCategoria=categoria.idCategoria,
            idEmpresa=categoria.idEmpresa,
            nombreCategoria=categoria.nombreCategoria,
            descripcion=categoria.descripcion,
            isActivo=categoria.isActivo,
        )

    @staticmethod
    def listar(db: Session, incluir_inactivas: bool = True) -> list[CategoriaResponse]:
        categorias = CategoriaRepository.obtener_todas(
            db=db,
            incluir_inactivas=incluir_inactivas,
        )
        return [CategoriaService._response(categoria) for categoria in categorias]

    @staticmethod
    def obtener_por_id(db: Session, id_categoria: int) -> CategoriaResponse:
        categoria = CategoriaRepository.obtener_por_id(db, id_categoria)

        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada",
            )

        return CategoriaService._response(categoria)

    @staticmethod
    def crear(db: Session, datos: CategoriaCreateRequest) -> CategoriaResponse:
        empresa = EmpresaRepository.obtener_primera(db)

        if not empresa:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Primero debes configurar la empresa",
            )

        existente = CategoriaRepository.obtener_por_nombre(
            db=db,
            id_empresa=empresa.idEmpresa,
            nombre=datos.nombreCategoria,
        )

        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una categoría con ese nombre",
            )

        categoria = Categoria(
            idEmpresa=empresa.idEmpresa,
            nombreCategoria=datos.nombreCategoria,
            descripcion=datos.descripcion,
            isActivo=True,
        )

        CategoriaRepository.guardar(db, categoria)
        db.commit()
        db.refresh(categoria)

        return CategoriaService._response(categoria)

    @staticmethod
    def actualizar(
        db: Session,
        id_categoria: int,
        datos: CategoriaUpdateRequest,
    ) -> CategoriaResponse:
        categoria = CategoriaRepository.obtener_por_id(db, id_categoria)

        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada",
            )

        cambios = datos.model_dump(exclude_unset=True)

        if "nombreCategoria" in cambios:
            existente = CategoriaRepository.obtener_por_nombre(
                db=db,
                id_empresa=categoria.idEmpresa,
                nombre=cambios["nombreCategoria"],
            )
            if existente and existente.idCategoria != id_categoria:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Ya existe otra categoría con ese nombre",
                )

        for campo, valor in cambios.items():
            setattr(categoria, campo, valor)

        CategoriaRepository.guardar(db, categoria)
        db.commit()
        db.refresh(categoria)

        return CategoriaService._response(categoria)
