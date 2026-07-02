from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.producto import Producto
from app.repositories.empresa_repository import EmpresaRepository
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.producto_repository import ProductoRepository
from app.schemas.producto_schema import ProductoCreateRequest, ProductoResponse, ProductoUpdateRequest


class ProductoService:

    @staticmethod
    def _response(producto: Producto) -> ProductoResponse:
        return ProductoResponse(
            idProducto=producto.idProducto,
            idEmpresa=producto.idEmpresa,
            idCategoria=producto.idCategoria,
            categoria=producto.categoria.nombreCategoria if producto.categoria else None,
            codigoBarras=producto.codigoBarras,
            nombreProducto=producto.nombreProducto,
            precioVenta=producto.precioVenta,
            porcentajeIgv=producto.porcentajeIgv,
            isActivo=producto.isActivo,
        )

    @staticmethod
    def listar(db: Session, incluir_inactivos: bool = True) -> list[ProductoResponse]:
        productos = ProductoRepository.obtener_todos(db=db, incluir_inactivos=incluir_inactivos)
        return [ProductoService._response(producto) for producto in productos]

    @staticmethod
    def obtener_por_id(db: Session, id_producto: int) -> ProductoResponse:
        producto = ProductoRepository.obtener_por_id(db, id_producto)
        if not producto:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
        return ProductoService._response(producto)

    @staticmethod
    def obtener_por_codigo_barras(db: Session, codigo_barras: str) -> ProductoResponse:
        producto = ProductoRepository.obtener_por_codigo_barras(db, codigo_barras)
        if not producto:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
        return ProductoService._response(producto)

    @staticmethod
    def crear(db: Session, datos: ProductoCreateRequest) -> ProductoResponse:
        empresa = EmpresaRepository.obtener_primera(db)
        if not empresa:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Primero debes configurar la empresa")

        existente = ProductoRepository.obtener_por_codigo_barras(db=db, codigo_barras=datos.codigoBarras)
        if existente:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un producto con ese código de barras")

        id_categoria = datos.idCategoria
        if id_categoria is not None:
            categoria = CategoriaRepository.obtener_por_id(db, id_categoria)
            if not categoria or not categoria.isActivo:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La categoría indicada no existe o está inactiva")

        producto = Producto(
            idEmpresa=empresa.idEmpresa,
            idCategoria=id_categoria,
            codigoBarras=datos.codigoBarras,
            nombreProducto=datos.nombreProducto,
            precioVenta=datos.precioVenta,
            porcentajeIgv=datos.porcentajeIgv,
            isActivo=True,
        )

        ProductoRepository.guardar(db, producto)
        db.commit()
        producto_creado = ProductoRepository.obtener_por_id(db, producto.idProducto)
        return ProductoService._response(producto_creado)

    @staticmethod
    def actualizar(db: Session, id_producto: int, datos: ProductoUpdateRequest) -> ProductoResponse:
        producto = ProductoRepository.obtener_por_id(db, id_producto)
        if not producto:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

        cambios = datos.model_dump(exclude_unset=True)
        if "codigoBarras" in cambios:
            existente = ProductoRepository.obtener_por_codigo_barras(db=db, codigo_barras=cambios["codigoBarras"])
            if existente and existente.idProducto != id_producto:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe otro producto con ese código de barras")

        if "idCategoria" in cambios and cambios["idCategoria"] is not None:
            categoria = CategoriaRepository.obtener_por_id(db, cambios["idCategoria"])
            if not categoria or not categoria.isActivo:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La categoría indicada no existe o está inactiva")

        for campo, valor in cambios.items():
            setattr(producto, campo, valor)

        ProductoRepository.guardar(db, producto)
        db.commit()
        producto_actualizado = ProductoRepository.obtener_por_id(db, id_producto)
        return ProductoService._response(producto_actualizado)
