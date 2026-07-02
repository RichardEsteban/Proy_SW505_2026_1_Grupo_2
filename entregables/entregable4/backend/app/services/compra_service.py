from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.inventario_ubicacion import InventarioUbicacion
from app.models.movimiento_inventario import MovimientoInventario
from app.models.orden_compra import DetalleOrdenCompra, OrdenCompra
from app.models.usuario import Usuario
from app.repositories.inventario_repository import InventarioRepository
from app.repositories.movimiento_repository import MovimientoRepository
from app.repositories.orden_compra_repository import OrdenCompraRepository
from app.repositories.producto_repository import ProductoRepository
from app.repositories.proveedor_repository import ProveedorRepository
from app.repositories.ubicacion_repository import UbicacionRepository
from app.schemas.orden_compra_schema import (
    OrdenCompraCancelarRequest,
    OrdenCompraCreateRequest,
    OrdenCompraDetalleResponse,
    OrdenCompraResponse,
)


DOS_DECIMALES = Decimal("0.01")


class CompraService:

    @staticmethod
    def _money(valor: Decimal) -> Decimal:
        return valor.quantize(DOS_DECIMALES, rounding=ROUND_HALF_UP)

    @staticmethod
    def _calcular_importes_linea(precio_unitario: Decimal, cantidad: int, porcentaje_igv: Decimal) -> tuple[Decimal, Decimal, Decimal]:
        """Calcula importes con IGV incluido en el precio unitario.

        Ejemplo con IGV 18%: si el precio de compra ingresado es S/ 118.00,
        el subtotal será S/ 100.00, el IGV S/ 18.00 y el total S/ 118.00.
        """
        total = CompraService._money(precio_unitario * Decimal(cantidad))
        if porcentaje_igv > 0:
            divisor = Decimal("1.00") + porcentaje_igv / Decimal("100.00")
            subtotal = CompraService._money(total / divisor)
            igv = CompraService._money(total - subtotal)
        else:
            subtotal = total
            igv = Decimal("0.00")
        return subtotal, igv, total

    @staticmethod
    def _detalle_response(detalle: DetalleOrdenCompra) -> OrdenCompraDetalleResponse:
        porcentaje_igv = Decimal(str(detalle.producto.porcentajeIgv or 0))
        subtotal, igv, total_linea = CompraService._calcular_importes_linea(
            Decimal(detalle.precioCompraUnitario),
            detalle.cantidadPedida,
            porcentaje_igv,
        )

        return OrdenCompraDetalleResponse(
            idDetalleOrden=detalle.idDetalleOrden,
            idProducto=detalle.idProducto,
            codigoBarras=detalle.producto.codigoBarras,
            nombreProducto=detalle.producto.nombreProducto,
            cantidadPedida=detalle.cantidadPedida,
            cantidadRecibida=detalle.cantidadRecibida,
            precioCompraUnitario=detalle.precioCompraUnitario,
            subtotal=subtotal,
            igvAplicado=igv,
            totalLinea=total_linea,
        )

    @staticmethod
    def _response(orden_compra: OrdenCompra) -> OrdenCompraResponse:
        return OrdenCompraResponse(
            idOrdenCompra=orden_compra.idOrdenCompra,
            idProveedor=orden_compra.idProveedor,
            proveedor=orden_compra.proveedor.razonSocial,
            idUbicacionDestino=orden_compra.idUbicacionDestino,
            ubicacionDestino=orden_compra.ubicacion_destino.nombreUbicacion,
            idUsuarioComprador=orden_compra.idUsuarioComprador,
            usuarioComprador=orden_compra.usuario_comprador.correoElectronico,
            idUsuarioReceptor=orden_compra.idUsuarioReceptor,
            usuarioReceptor=(orden_compra.usuario_receptor.correoElectronico if orden_compra.usuario_receptor else None),
            fechaPedido=orden_compra.fechaPedido,
            fechaRecepcion=orden_compra.fechaRecepcion,
            estado=orden_compra.estado,
            totalNeto=orden_compra.totalNeto,
            totalIgv=orden_compra.totalIgv,
            totalCompra=orden_compra.totalCompra,
            detalles=[CompraService._detalle_response(detalle) for detalle in orden_compra.detalles],
        )

    @staticmethod
    def _resolver_ubicacion_destino(usuario_actual: Usuario, id_ubicacion_destino: int | None) -> int:
        return id_ubicacion_destino or usuario_actual.idUbicacion

    @staticmethod
    def crear(db: Session, datos: OrdenCompraCreateRequest, usuario_actual: Usuario) -> OrdenCompraResponse:
        id_ubicacion_destino = CompraService._resolver_ubicacion_destino(usuario_actual, datos.idUbicacionDestino)

        ubicacion = UbicacionRepository.obtener_por_id(db, id_ubicacion_destino)
        if not ubicacion or not ubicacion.isActivo:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La ubicación destino no existe o está inactiva")

        proveedor = ProveedorRepository.obtener_por_id(db, datos.idProveedor)
        if not proveedor or not proveedor.isActivo:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El proveedor no existe o está inactivo")

        detalles_por_producto: dict[int, dict] = {}
        for detalle in datos.detalles:
            producto = ProductoRepository.obtener_por_id(db, detalle.idProducto)
            if not producto or not producto.isActivo:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"El producto {detalle.idProducto} no existe o está inactivo")

            if detalle.idProducto not in detalles_por_producto:
                detalles_por_producto[detalle.idProducto] = {"producto": producto, "cantidad": 0, "precio": Decimal(detalle.precioCompraUnitario)}
            detalles_por_producto[detalle.idProducto]["cantidad"] += detalle.cantidadPedida

        total_neto = Decimal("0.00")
        total_igv = Decimal("0.00")
        total_compra = Decimal("0.00")
        detalles_calculados = []

        for id_producto, item in detalles_por_producto.items():
            # El precio ingresado ya incluye IGV; aquí se separa subtotal/IGV para reportes.
            producto = item["producto"]
            cantidad = item["cantidad"]
            precio_unitario = CompraService._money(Decimal(item["precio"]))
            porcentaje_igv = Decimal(str(producto.porcentajeIgv or 0))
            subtotal_linea, igv_linea, total_linea = CompraService._calcular_importes_linea(
                precio_unitario,
                cantidad,
                porcentaje_igv,
            )
            total_neto += subtotal_linea
            total_igv += igv_linea
            total_compra += total_linea
            detalles_calculados.append({
                "idProducto": id_producto,
                "cantidadPedida": cantidad,
                "precioCompraUnitario": precio_unitario,
            })

        orden_compra = OrdenCompra(
            idProveedor=datos.idProveedor,
            idUbicacionDestino=id_ubicacion_destino,
            idUsuarioComprador=usuario_actual.idUsuario,
            totalNeto=CompraService._money(total_neto),
            totalIgv=CompraService._money(total_igv),
            totalCompra=CompraService._money(total_compra),
            estado="SOLICITADO",
        )
        OrdenCompraRepository.guardar(db, orden_compra)

        for detalle_calculado in detalles_calculados:
            db.add(DetalleOrdenCompra(
                idOrdenCompra=orden_compra.idOrdenCompra,
                idProducto=detalle_calculado["idProducto"],
                cantidadPedida=detalle_calculado["cantidadPedida"],
                cantidadRecibida=0,
                precioCompraUnitario=detalle_calculado["precioCompraUnitario"],
            ))

        db.commit()
        orden_creada = OrdenCompraRepository.obtener_por_id(db, orden_compra.idOrdenCompra)
        return CompraService._response(orden_creada)

    @staticmethod
    def enviar(db: Session, id_orden_compra: int, usuario_actual: Usuario) -> OrdenCompraResponse:
        orden_compra = OrdenCompraRepository.obtener_por_id(db, id_orden_compra)
        if not orden_compra:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Orden de compra no encontrada")
        if orden_compra.estado != "SOLICITADO":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Solo se pueden enviar órdenes solicitadas")

        orden_compra.estado = "EN_TRANSITO"
        OrdenCompraRepository.guardar(db, orden_compra)
        db.commit()
        return CompraService._response(OrdenCompraRepository.obtener_por_id(db, id_orden_compra))

    @staticmethod
    def recibir(db: Session, id_orden_compra: int, usuario_actual: Usuario) -> OrdenCompraResponse:
        orden_compra = OrdenCompraRepository.obtener_por_id(db, id_orden_compra)
        if not orden_compra:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Orden de compra no encontrada")
        if orden_compra.estado not in ("SOLICITADO", "EN_TRANSITO"):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Solo se pueden recepcionar órdenes pendientes o en tránsito")

        for detalle in orden_compra.detalles:
            inventario = InventarioRepository.obtener_por_ubicacion_producto(db, orden_compra.idUbicacionDestino, detalle.idProducto)
            if not inventario:
                inventario = InventarioUbicacion(idUbicacion=orden_compra.idUbicacionDestino, idProducto=detalle.idProducto, stockDisponible=0, stockMinimo=0)
                InventarioRepository.guardar(db, inventario)

            cantidad_por_recibir = detalle.cantidadPedida - detalle.cantidadRecibida
            if cantidad_por_recibir <= 0:
                continue

            inventario.stockDisponible += cantidad_por_recibir
            InventarioRepository.guardar(db, inventario)
            detalle.cantidadRecibida = detalle.cantidadPedida

            MovimientoRepository.guardar(db, MovimientoInventario(
                idUbicacion=orden_compra.idUbicacionDestino,
                idProducto=detalle.idProducto,
                idUsuario=usuario_actual.idUsuario,
                cantidad=cantidad_por_recibir,
                tipoMovimiento="INGRESO",
                motivoMovimiento="COMPRA_PROVEEDOR",
                tipoReferencia="ORDEN_COMPRA",
                idReferencia=orden_compra.idOrdenCompra,
            ))

        orden_compra.estado = "RECIBIDO"
        orden_compra.idUsuarioReceptor = usuario_actual.idUsuario
        orden_compra.fechaRecepcion = datetime.now()
        OrdenCompraRepository.guardar(db, orden_compra)
        db.commit()
        return CompraService._response(OrdenCompraRepository.obtener_por_id(db, id_orden_compra))

    @staticmethod
    def cancelar(db: Session, id_orden_compra: int, datos: OrdenCompraCancelarRequest, usuario_actual: Usuario) -> OrdenCompraResponse:
        orden_compra = OrdenCompraRepository.obtener_por_id(db, id_orden_compra)
        if not orden_compra:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Orden de compra no encontrada")
        if orden_compra.estado in ("RECIBIDO", "CANCELADO"):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No se puede cancelar una orden recibida o ya cancelada")

        orden_compra.estado = "CANCELADO"
        OrdenCompraRepository.guardar(db, orden_compra)
        db.commit()
        return CompraService._response(OrdenCompraRepository.obtener_por_id(db, id_orden_compra))

    anular = cancelar

    @staticmethod
    def obtener_por_id(db: Session, id_orden_compra: int) -> OrdenCompraResponse:
        orden_compra = OrdenCompraRepository.obtener_por_id(db, id_orden_compra)
        if not orden_compra:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Orden de compra no encontrada")
        return CompraService._response(orden_compra)

    @staticmethod
    def listar(
        db: Session,
        id_proveedor: int | None = None,
        id_ubicacion_destino: int | None = None,
        estado: str | None = None,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        limite: int = 100,
    ) -> list[OrdenCompraResponse]:
        ordenes = OrdenCompraRepository.obtener_todas(db, id_proveedor, id_ubicacion_destino, estado, desde, hasta, limite)
        return [CompraService._response(orden) for orden in ordenes]
