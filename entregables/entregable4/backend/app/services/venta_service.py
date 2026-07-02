from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.constants import Roles
from app.models.movimiento_inventario import MovimientoInventario
from app.models.usuario import Usuario
from app.models.venta import DetalleVenta, Venta
from app.repositories.cliente_repository import ClienteRepository
from app.repositories.inventario_repository import InventarioRepository
from app.repositories.metodo_pago_repository import MetodoPagoRepository
from app.repositories.movimiento_repository import MovimientoRepository
from app.repositories.producto_repository import ProductoRepository
from app.repositories.ubicacion_repository import UbicacionRepository
from app.repositories.venta_repository import VentaRepository
from app.schemas.venta_schema import (
    VentaCreateRequest,
    VentaDetalleResponse,
    VentaResponse,
)
from app.services.inventario_service import InventarioService
from app.services.cliente_service import ClienteService


DOS_DECIMALES = Decimal("0.01")


class VentaService:

    @staticmethod
    def _usuario_es_global(usuario: Usuario) -> bool:
        return usuario.rol.nombreRol in (Roles.ADMIN, Roles.SUPERVISOR_ALMACEN)

    @staticmethod
    def _money(valor: Decimal) -> Decimal:
        return valor.quantize(DOS_DECIMALES, rounding=ROUND_HALF_UP)

    @staticmethod
    def _detalle_response(detalle: DetalleVenta) -> VentaDetalleResponse:
        return VentaDetalleResponse(
            idDetalleVenta=detalle.idDetalleVenta,
            idProducto=detalle.idProducto,
            codigoBarras=detalle.producto.codigoBarras,
            nombreProducto=detalle.producto.nombreProducto,
            cantidad=detalle.cantidad,
            precioUnitarioFacturado=detalle.precioUnitarioFacturado,
            subtotal=detalle.subtotal,
            igvAplicado=detalle.igvAplicado,
            totalLinea=detalle.subtotal + detalle.igvAplicado,
        )

    @staticmethod
    def _response(venta: Venta) -> VentaResponse:
        return VentaResponse(
            idVenta=venta.idVenta,
            idUbicacion=venta.idUbicacion,
            ubicacion=venta.ubicacion.nombreUbicacion,
            idUsuario=venta.idUsuario,
            usuario=venta.usuario.correoElectronico,
            idCliente=venta.idCliente,
            cliente=ClienteService.nombre_mostrar(venta.cliente) if venta.cliente else None,
            idMetodoPago=venta.idMetodoPago,
            metodoPago=venta.metodo_pago.nombreMetodo,
            fechaHora=venta.fechaHora,
            subtotalVenta=venta.subtotalVenta,
            totalIgv=venta.totalIgv,
            totalVenta=venta.totalVenta,
            pdf_url=venta.pdf_url,
            detalles=[VentaService._detalle_response(detalle) for detalle in venta.detalles],
        )

    @staticmethod
    def _resolver_ubicacion_venta(usuario_actual: Usuario, id_ubicacion: int | None) -> int:
        if VentaService._usuario_es_global(usuario_actual):
            return id_ubicacion or usuario_actual.idUbicacion

        if id_ubicacion is not None and id_ubicacion != usuario_actual.idUbicacion:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo puedes registrar ventas en tu propia ubicación",
            )

        return usuario_actual.idUbicacion

    @staticmethod
    def crear(db: Session, datos: VentaCreateRequest, usuario_actual: Usuario) -> VentaResponse:
        id_ubicacion = VentaService._resolver_ubicacion_venta(
            usuario_actual=usuario_actual,
            id_ubicacion=datos.idUbicacion,
        )

        ubicacion = UbicacionRepository.obtener_por_id(db, id_ubicacion)
        if not ubicacion or not ubicacion.isActivo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La ubicación de venta no existe o está inactiva",
            )

        metodo_pago = MetodoPagoRepository.obtener_por_id(db, datos.idMetodoPago)
        if not metodo_pago or not metodo_pago.isActivo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El método de pago no existe o está inactivo",
            )

        if datos.idCliente is not None:
            cliente = ClienteRepository.obtener_por_id(db, datos.idCliente)
            if not cliente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El cliente no existe o está inactivo",
                )

        cantidades_por_producto: dict[int, int] = {}
        for detalle in datos.detalles:
            cantidades_por_producto[detalle.idProducto] = (
                cantidades_por_producto.get(detalle.idProducto, 0) + detalle.cantidad
            )

        productos = {}
        inventarios = {}
        for id_producto, cantidad in cantidades_por_producto.items():
            producto = ProductoRepository.obtener_por_id(db, id_producto)
            if not producto or not producto.isActivo:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El producto {id_producto} no existe o está inactivo",
                )

            inventario = InventarioRepository.obtener_por_ubicacion_producto(
                db=db,
                id_ubicacion=id_ubicacion,
                id_producto=id_producto,
            )
            if not inventario or inventario.stockDisponible < cantidad:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Stock insuficiente para el producto {producto.nombreProducto}",
                )

            productos[id_producto] = producto
            inventarios[id_producto] = inventario

        subtotal_venta = Decimal("0.00")
        total_igv = Decimal("0.00")
        total_venta = Decimal("0.00")
        detalles_calculados = []

        for id_producto, cantidad in cantidades_por_producto.items():
            producto = productos[id_producto]
            precio_unitario = VentaService._money(Decimal(str(producto.precioVenta)))
            porcentaje_igv = Decimal(str(producto.porcentajeIgv or 0))
            total_linea = VentaService._money(precio_unitario * Decimal(cantidad))

            if porcentaje_igv > 0:
                divisor = Decimal("1.00") + (porcentaje_igv / Decimal("100.00"))
                subtotal_linea = VentaService._money(total_linea / divisor)
                igv_linea = VentaService._money(total_linea - subtotal_linea)
            else:
                subtotal_linea = total_linea
                igv_linea = Decimal("0.00")

            subtotal_venta += subtotal_linea
            total_igv += igv_linea
            total_venta += total_linea
            detalles_calculados.append({
                "idProducto": id_producto,
                "cantidad": cantidad,
                "precioUnitarioFacturado": precio_unitario,
                "subtotal": subtotal_linea,
                "igvAplicado": igv_linea,
                "totalLinea": total_linea,
            })

        venta = Venta(
            idUbicacion=id_ubicacion,
            idUsuario=usuario_actual.idUsuario,
            idCliente=datos.idCliente,
            idMetodoPago=datos.idMetodoPago,
            subtotalVenta=VentaService._money(subtotal_venta),
            totalIgv=VentaService._money(total_igv),
            totalVenta=VentaService._money(total_venta),
        )
        VentaRepository.guardar(db, venta)

        for detalle_calculado in detalles_calculados:
            detalle = DetalleVenta(
                idVenta=venta.idVenta,
                idProducto=detalle_calculado["idProducto"],
                cantidad=detalle_calculado["cantidad"],
                precioUnitarioFacturado=detalle_calculado["precioUnitarioFacturado"],
                subtotal=detalle_calculado["subtotal"],
                igvAplicado=detalle_calculado["igvAplicado"],
            )
            db.add(detalle)

            inventario = inventarios[detalle_calculado["idProducto"]]
            inventario.stockDisponible -= detalle_calculado["cantidad"]
            InventarioRepository.guardar(db, inventario)

            movimiento = MovimientoInventario(
                idUbicacion=id_ubicacion,
                idProducto=detalle_calculado["idProducto"],
                idUsuario=usuario_actual.idUsuario,
                cantidad=detalle_calculado["cantidad"],
                tipoMovimiento="SALIDA",
                motivoMovimiento="VENTA",
                tipoReferencia="VENTA",
                idReferencia=venta.idVenta,
            )
            MovimientoRepository.guardar(db, movimiento)
            InventarioService._crear_alerta_si_corresponde(db, inventario)

        db.commit()

        venta_creada = VentaRepository.obtener_por_id(db, venta.idVenta)
        return VentaService._response(venta_creada)

    @staticmethod
    def obtener_por_id(db: Session, id_venta: int, usuario_actual: Usuario) -> VentaResponse:
        venta = VentaRepository.obtener_por_id(db, id_venta)
        if not venta:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venta no encontrada")

        if not VentaService._usuario_es_global(usuario_actual) and venta.idUbicacion != usuario_actual.idUbicacion:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo puedes consultar ventas de tu propia ubicación",
            )

        return VentaService._response(venta)

    @staticmethod
    def listar(
        db: Session,
        usuario_actual: Usuario,
        id_ubicacion: int | None = None,
        id_usuario: int | None = None,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        limite: int = 100,
    ) -> list[VentaResponse]:
        if not VentaService._usuario_es_global(usuario_actual):
            if id_ubicacion is not None and id_ubicacion != usuario_actual.idUbicacion:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Solo puedes consultar ventas de tu propia ubicación",
                )
            id_ubicacion = usuario_actual.idUbicacion

        ventas = VentaRepository.obtener_todas(
            db=db,
            id_ubicacion=id_ubicacion,
            id_usuario=id_usuario,
            desde=desde,
            hasta=hasta,
            limite=limite,
        )
        return [VentaService._response(venta) for venta in ventas]
