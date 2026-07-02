from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.constants import Roles
from app.models.alerta_stock import AlertaStock
from app.models.inventario_ubicacion import InventarioUbicacion
from app.models.movimiento_inventario import MovimientoInventario
from app.models.usuario import Usuario
from app.repositories.alerta_repository import AlertaRepository
from app.repositories.inventario_repository import InventarioRepository
from app.repositories.movimiento_repository import MovimientoRepository
from app.repositories.producto_repository import ProductoRepository
from app.repositories.ubicacion_repository import UbicacionRepository
from app.schemas.inventario_schema import (
    InventarioCreateRequest,
    InventarioResponse,
    InventarioStockMinimoUpdateRequest,
    MovimientoInventarioCreateRequest,
    MovimientoInventarioResponse,
)


class InventarioService:

    @staticmethod
    def _usuario_es_global(usuario: Usuario) -> bool:
        return usuario.rol.nombreRol in (Roles.ADMIN, Roles.SUPERVISOR_ALMACEN)

    @staticmethod
    def _validar_acceso_ubicacion(usuario: Usuario, id_ubicacion: int):
        if InventarioService._usuario_es_global(usuario):
            return

        if usuario.idUbicacion != id_ubicacion:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo puedes consultar el inventario de tu ubicación",
            )

    @staticmethod
    def _estado_stock(inventario: InventarioUbicacion) -> str:
        if inventario.stockDisponible == 0:
            return "STOCK_AGOTADO"

        if inventario.stockDisponible <= inventario.stockMinimo:
            return "STOCK_MINIMO"

        return "NORMAL"

    @staticmethod
    def _response(inventario: InventarioUbicacion) -> InventarioResponse:
        producto = inventario.producto
        ubicacion = inventario.ubicacion

        return InventarioResponse(
            idInventario=inventario.idInventario,
            idUbicacion=inventario.idUbicacion,
            ubicacion=ubicacion.nombreUbicacion,
            tipoUbicacion=ubicacion.tipoUbicacion,
            idProducto=inventario.idProducto,
            codigoBarras=producto.codigoBarras,
            producto=producto.nombreProducto,
            categoria=producto.categoria.nombreCategoria if producto.categoria else None,
            stockDisponible=inventario.stockDisponible,
            stockMinimo=inventario.stockMinimo,
            estadoStock=InventarioService._estado_stock(inventario),
        )

    @staticmethod
    def _movimiento_response(movimiento: MovimientoInventario) -> MovimientoInventarioResponse:
        return MovimientoInventarioResponse(
            idMovimiento=movimiento.idMovimiento,
            idUbicacion=movimiento.idUbicacion,
            ubicacion=movimiento.ubicacion.nombreUbicacion,
            idProducto=movimiento.idProducto,
            producto=movimiento.producto.nombreProducto,
            idUsuario=movimiento.idUsuario,
            usuario=movimiento.usuario.correoElectronico,
            cantidad=movimiento.cantidad,
            tipoMovimiento=movimiento.tipoMovimiento,
            motivoMovimiento=movimiento.motivoMovimiento,
            tipoReferencia=movimiento.tipoReferencia,
            idReferencia=movimiento.idReferencia,
            fechaHora=movimiento.fechaHora,
        )

    @staticmethod
    def _validar_ubicacion_activa(db: Session, id_ubicacion: int):
        ubicacion = UbicacionRepository.obtener_por_id(db, id_ubicacion)

        if not ubicacion:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La ubicación indicada no existe",
            )

        if not ubicacion.isActivo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puedes operar con una ubicación inactiva",
            )

        return ubicacion

    @staticmethod
    def _validar_producto_activo(db: Session, id_producto: int):
        producto = ProductoRepository.obtener_por_id(db, id_producto)

        if not producto:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El producto indicado no existe",
            )

        if not producto.isActivo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puedes operar con un producto inactivo",
            )

        return producto

    @staticmethod
    def _crear_alerta_si_corresponde(db: Session, inventario: InventarioUbicacion):
        tipo_alerta = None

        if inventario.stockDisponible == 0:
            tipo_alerta = "STOCK_AGOTADO"
        elif inventario.stockDisponible <= inventario.stockMinimo:
            tipo_alerta = "STOCK_MINIMO"

        if tipo_alerta is None:
            return

        alerta_pendiente = AlertaRepository.obtener_pendiente_por_producto(
            db=db,
            id_ubicacion=inventario.idUbicacion,
            id_producto=inventario.idProducto,
            tipo_alerta=tipo_alerta,
        )

        if alerta_pendiente:
            alerta_pendiente.cantidadActual = inventario.stockDisponible
            alerta_pendiente.stockReferencia = inventario.stockMinimo
            AlertaRepository.guardar(db, alerta_pendiente)
            return

        alerta = AlertaStock(
            idUbicacion=inventario.idUbicacion,
            idProducto=inventario.idProducto,
            tipoAlerta=tipo_alerta,
            cantidadActual=inventario.stockDisponible,
            stockReferencia=inventario.stockMinimo,
            estado="PENDIENTE",
        )
        AlertaRepository.guardar(db, alerta)

    @staticmethod
    def listar(
        db: Session,
        usuario_actual: Usuario,
        id_ubicacion: int | None = None,
        id_producto: int | None = None,
        solo_bajo_minimo: bool = False,
    ) -> list[InventarioResponse]:
        if not InventarioService._usuario_es_global(usuario_actual):
            if id_ubicacion is not None and id_ubicacion != usuario_actual.idUbicacion:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Solo puedes consultar el inventario de tu ubicación",
                )
            id_ubicacion = usuario_actual.idUbicacion

        inventarios = InventarioRepository.obtener_todos(
            db=db,
            id_ubicacion=id_ubicacion,
            id_producto=id_producto,
            solo_bajo_minimo=solo_bajo_minimo,
        )
        return [InventarioService._response(inventario) for inventario in inventarios]

    @staticmethod
    def obtener_por_id(
        db: Session,
        id_inventario: int,
        usuario_actual: Usuario,
    ) -> InventarioResponse:
        inventario = InventarioRepository.obtener_por_id(db, id_inventario)

        if not inventario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Registro de inventario no encontrado",
            )

        InventarioService._validar_acceso_ubicacion(usuario_actual, inventario.idUbicacion)
        return InventarioService._response(inventario)

    @staticmethod
    def crear_stock_inicial(
        db: Session,
        datos: InventarioCreateRequest,
        usuario_actual: Usuario,
    ) -> InventarioResponse:
        InventarioService._validar_ubicacion_activa(db, datos.idUbicacion)
        InventarioService._validar_producto_activo(db, datos.idProducto)

        existente = InventarioRepository.obtener_por_ubicacion_producto(
            db=db,
            id_ubicacion=datos.idUbicacion,
            id_producto=datos.idProducto,
        )

        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Este producto ya tiene inventario creado en esa ubicación",
            )

        inventario = InventarioUbicacion(
            idUbicacion=datos.idUbicacion,
            idProducto=datos.idProducto,
            stockDisponible=datos.stockDisponible,
            stockMinimo=datos.stockMinimo,
        )
        InventarioRepository.guardar(db, inventario)

        if datos.stockDisponible > 0:
            movimiento = MovimientoInventario(
                idUbicacion=datos.idUbicacion,
                idProducto=datos.idProducto,
                idUsuario=usuario_actual.idUsuario,
                cantidad=datos.stockDisponible,
                tipoMovimiento="INGRESO",
                motivoMovimiento="AJUSTE",
            )
            MovimientoRepository.guardar(db, movimiento)

        InventarioService._crear_alerta_si_corresponde(db, inventario)
        db.commit()

        inventario_creado = InventarioRepository.obtener_por_id(db, inventario.idInventario)
        return InventarioService._response(inventario_creado)

    @staticmethod
    def actualizar_stock_minimo(
        db: Session,
        id_inventario: int,
        datos: InventarioStockMinimoUpdateRequest,
        usuario_actual: Usuario,
    ) -> InventarioResponse:
        inventario = InventarioRepository.obtener_por_id(db, id_inventario)

        if not inventario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Registro de inventario no encontrado",
            )

        InventarioService._validar_acceso_ubicacion(usuario_actual, inventario.idUbicacion)
        inventario.stockMinimo = datos.stockMinimo
        InventarioRepository.guardar(db, inventario)
        InventarioService._crear_alerta_si_corresponde(db, inventario)
        db.commit()

        inventario_actualizado = InventarioRepository.obtener_por_id(db, id_inventario)
        return InventarioService._response(inventario_actualizado)

    @staticmethod
    def registrar_movimiento(
        db: Session,
        datos: MovimientoInventarioCreateRequest,
        usuario_actual: Usuario,
    ) -> MovimientoInventarioResponse:
        InventarioService._validar_ubicacion_activa(db, datos.idUbicacion)
        InventarioService._validar_producto_activo(db, datos.idProducto)

        inventario = InventarioRepository.obtener_por_ubicacion_producto(
            db=db,
            id_ubicacion=datos.idUbicacion,
            id_producto=datos.idProducto,
        )

        if not inventario:
            if datos.tipoMovimiento == "SALIDA":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No existe inventario para retirar stock de ese producto en esa ubicación",
                )

            inventario = InventarioUbicacion(
                idUbicacion=datos.idUbicacion,
                idProducto=datos.idProducto,
                stockDisponible=0,
                stockMinimo=0,
            )
            InventarioRepository.guardar(db, inventario)

        if datos.tipoMovimiento == "INGRESO":
            inventario.stockDisponible += datos.cantidad
        else:
            if inventario.stockDisponible < datos.cantidad:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Stock insuficiente para registrar la salida",
                )
            inventario.stockDisponible -= datos.cantidad

        InventarioRepository.guardar(db, inventario)

        movimiento = MovimientoInventario(
            idUbicacion=datos.idUbicacion,
            idProducto=datos.idProducto,
            idUsuario=usuario_actual.idUsuario,
            cantidad=datos.cantidad,
            tipoMovimiento=datos.tipoMovimiento,
            motivoMovimiento=datos.motivoMovimiento,
            tipoReferencia=datos.tipoReferencia,
            idReferencia=datos.idReferencia,
        )
        MovimientoRepository.guardar(db, movimiento)
        InventarioService._crear_alerta_si_corresponde(db, inventario)
        db.commit()

        movimiento_creado = MovimientoRepository.obtener_por_id(db, movimiento.idMovimiento)
        return InventarioService._movimiento_response(movimiento_creado)

    @staticmethod
    def listar_movimientos(
        db: Session,
        usuario_actual: Usuario,
        id_ubicacion: int | None = None,
        id_producto: int | None = None,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        limite: int = 100,
    ) -> list[MovimientoInventarioResponse]:
        if not InventarioService._usuario_es_global(usuario_actual):
            if id_ubicacion is not None and id_ubicacion != usuario_actual.idUbicacion:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Solo puedes consultar movimientos de tu ubicación",
                )
            id_ubicacion = usuario_actual.idUbicacion

        movimientos = MovimientoRepository.obtener_todos(
            db=db,
            id_ubicacion=id_ubicacion,
            id_producto=id_producto,
            desde=desde,
            hasta=hasta,
            limite=limite,
        )
        return [InventarioService._movimiento_response(movimiento) for movimiento in movimientos]
