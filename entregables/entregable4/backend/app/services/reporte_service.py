from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.core.constants import Roles
from app.models.alerta_stock import AlertaStock
from app.models.inventario_ubicacion import InventarioUbicacion
from app.models.movimiento_inventario import MovimientoInventario
from app.models.orden_compra import OrdenCompra
from app.models.producto import Producto
from app.models.solicitud_reposicion import SolicitudReposicion
from app.models.ubicacion import Ubicacion
from app.models.usuario import Usuario
from app.models.venta import DetalleVenta, Venta
from app.schemas.reporte_schema import (
    ReporteCompraResponse,
    ReporteKardexResponse,
    ReporteProductoVendidoResponse,
    ReporteReposicionPorEstadoResponse,
    ReporteResumenResponse,
    ReporteStockBajoResponse,
    ReporteVentaPorFechaResponse,
)


class ReporteService:

    @staticmethod
    def _usuario_es_global(usuario: Usuario) -> bool:
        return usuario.rol.nombreRol in (Roles.ADMIN, Roles.SUPERVISOR_ALMACEN)

    @staticmethod
    def _resolver_ubicacion(usuario: Usuario, id_ubicacion: int | None) -> int | None:
        if ReporteService._usuario_es_global(usuario):
            return id_ubicacion
        if id_ubicacion is not None and id_ubicacion != usuario.idUbicacion:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo puedes consultar reportes de tu propia ubicación")
        return usuario.idUbicacion

    @staticmethod
    def resumen(db: Session, usuario_actual: Usuario, id_ubicacion: int | None = None, desde: datetime | None = None, hasta: datetime | None = None) -> ReporteResumenResponse:
        id_ubicacion = ReporteService._resolver_ubicacion(usuario_actual, id_ubicacion)

        stmt_ventas = select(func.count(Venta.idVenta), func.coalesce(func.sum(Venta.totalVenta), 0))
        if id_ubicacion is not None:
            stmt_ventas = stmt_ventas.where(Venta.idUbicacion == id_ubicacion)
        if desde is not None:
            stmt_ventas = stmt_ventas.where(Venta.fechaHora >= desde)
        if hasta is not None:
            stmt_ventas = stmt_ventas.where(Venta.fechaHora <= hasta)
        cantidad_ventas, total_ventas = db.execute(stmt_ventas).one()
        total_ventas = Decimal(str(total_ventas or 0))
        ticket_promedio = total_ventas / Decimal(cantidad_ventas) if cantidad_ventas else Decimal("0.00")

        stmt_productos_vendidos = select(func.coalesce(func.sum(DetalleVenta.cantidad), 0)).join(
            Venta, Venta.idVenta == DetalleVenta.idVenta
        )
        if id_ubicacion is not None:
            stmt_productos_vendidos = stmt_productos_vendidos.where(Venta.idUbicacion == id_ubicacion)
        if desde is not None:
            stmt_productos_vendidos = stmt_productos_vendidos.where(Venta.fechaHora >= desde)
        if hasta is not None:
            stmt_productos_vendidos = stmt_productos_vendidos.where(Venta.fechaHora <= hasta)
        productos_vendidos = int(db.execute(stmt_productos_vendidos).scalar() or 0)

        stmt_stock = select(func.count(InventarioUbicacion.idInventario)).where(
            InventarioUbicacion.stockDisponible <= InventarioUbicacion.stockMinimo
        )
        if id_ubicacion is not None:
            stmt_stock = stmt_stock.where(InventarioUbicacion.idUbicacion == id_ubicacion)
        productos_stock_bajo = db.execute(stmt_stock).scalar() or 0

        stmt_alertas = select(func.count(AlertaStock.idAlerta)).where(AlertaStock.estado == "PENDIENTE")
        if id_ubicacion is not None:
            stmt_alertas = stmt_alertas.where(AlertaStock.idUbicacion == id_ubicacion)
        alertas_pendientes = db.execute(stmt_alertas).scalar() or 0

        stmt_compras = select(func.count(OrdenCompra.idOrdenCompra)).where(OrdenCompra.estado.in_(["SOLICITADO", "EN_TRANSITO"]))
        if id_ubicacion is not None:
            stmt_compras = stmt_compras.where(OrdenCompra.idUbicacionDestino == id_ubicacion)
        ordenes_abiertas = db.execute(stmt_compras).scalar() or 0

        stmt_repos = select(func.count(SolicitudReposicion.idSolicitud)).where(
            SolicitudReposicion.estado.in_(["ENVIADO", "EN_REVISION", "ACEPTADO", "EN_TRANSITO"])
        )
        if id_ubicacion is not None:
            stmt_repos = stmt_repos.where(SolicitudReposicion.idUbicacionDestino == id_ubicacion)
        reposiciones_abiertas = db.execute(stmt_repos).scalar() or 0

        return ReporteResumenResponse(
            totalVentas=total_ventas,
            cantidadVentas=cantidad_ventas,
            productosVendidos=productos_vendidos,
            ticketPromedio=ticket_promedio,
            productosConStockBajo=productos_stock_bajo,
            alertasPendientes=alertas_pendientes,
            ordenesCompraAbiertas=ordenes_abiertas,
            reposicionesAbiertas=reposiciones_abiertas,
        )

    @staticmethod
    def ventas_por_fecha(db: Session, usuario_actual: Usuario, id_ubicacion: int | None = None, desde: datetime | None = None, hasta: datetime | None = None) -> list[ReporteVentaPorFechaResponse]:
        id_ubicacion = ReporteService._resolver_ubicacion(usuario_actual, id_ubicacion)
        fecha = func.date(Venta.fechaHora)
        stmt = select(
            fecha.label("fecha"),
            func.count(Venta.idVenta).label("cantidad"),
            func.coalesce(func.sum(Venta.subtotalVenta), 0).label("subtotal"),
            func.coalesce(func.sum(Venta.totalIgv), 0).label("igv"),
            func.coalesce(func.sum(Venta.totalVenta), 0).label("total"),
        ).group_by(fecha).order_by(fecha)
        if id_ubicacion is not None:
            stmt = stmt.where(Venta.idUbicacion == id_ubicacion)
        if desde is not None:
            stmt = stmt.where(Venta.fechaHora >= desde)
        if hasta is not None:
            stmt = stmt.where(Venta.fechaHora <= hasta)

        return [
            ReporteVentaPorFechaResponse(
                fecha=fila.fecha,
                cantidadVentas=fila.cantidad,
                subtotalVenta=Decimal(str(fila.subtotal or 0)),
                totalIgv=Decimal(str(fila.igv or 0)),
                totalVenta=Decimal(str(fila.total or 0)),
            )
            for fila in db.execute(stmt).all()
        ]

    @staticmethod
    def productos_mas_vendidos(db: Session, usuario_actual: Usuario, id_ubicacion: int | None = None, desde: datetime | None = None, hasta: datetime | None = None, limite: int = 20) -> list[ReporteProductoVendidoResponse]:
        id_ubicacion = ReporteService._resolver_ubicacion(usuario_actual, id_ubicacion)
        total_linea = DetalleVenta.subtotal + DetalleVenta.igvAplicado
        stmt = (
            select(
                Producto.idProducto,
                Producto.codigoBarras,
                Producto.nombreProducto,
                func.coalesce(func.sum(DetalleVenta.cantidad), 0).label("cantidad"),
                func.coalesce(func.sum(total_linea), 0).label("total"),
            )
            .join(DetalleVenta, DetalleVenta.idProducto == Producto.idProducto)
            .join(Venta, Venta.idVenta == DetalleVenta.idVenta)
            .group_by(Producto.idProducto, Producto.codigoBarras, Producto.nombreProducto)
            .order_by(func.sum(DetalleVenta.cantidad).desc())
            .limit(limite)
        )
        if id_ubicacion is not None:
            stmt = stmt.where(Venta.idUbicacion == id_ubicacion)
        if desde is not None:
            stmt = stmt.where(Venta.fechaHora >= desde)
        if hasta is not None:
            stmt = stmt.where(Venta.fechaHora <= hasta)

        return [
            ReporteProductoVendidoResponse(
                idProducto=fila.idProducto,
                codigoBarras=fila.codigoBarras,
                nombreProducto=fila.nombreProducto,
                cantidadVendida=int(fila.cantidad or 0),
                totalVendido=Decimal(str(fila.total or 0)),
            )
            for fila in db.execute(stmt).all()
        ]

    @staticmethod
    def stock_bajo(db: Session, usuario_actual: Usuario, id_ubicacion: int | None = None) -> list[ReporteStockBajoResponse]:
        id_ubicacion = ReporteService._resolver_ubicacion(usuario_actual, id_ubicacion)
        stmt = (
            select(InventarioUbicacion)
            .options(joinedload(InventarioUbicacion.ubicacion), joinedload(InventarioUbicacion.producto))
            .where(InventarioUbicacion.stockDisponible <= InventarioUbicacion.stockMinimo)
            .order_by(InventarioUbicacion.stockDisponible, InventarioUbicacion.idUbicacion)
        )
        if id_ubicacion is not None:
            stmt = stmt.where(InventarioUbicacion.idUbicacion == id_ubicacion)

        data = []
        for inv in db.execute(stmt).scalars().all():
            estado = "STOCK_AGOTADO" if inv.stockDisponible == 0 else "STOCK_MINIMO"
            data.append(ReporteStockBajoResponse(
                idInventario=inv.idInventario,
                idUbicacion=inv.idUbicacion,
                ubicacion=inv.ubicacion.nombreUbicacion,
                idProducto=inv.idProducto,
                codigoBarras=inv.producto.codigoBarras,
                producto=inv.producto.nombreProducto,
                stockDisponible=inv.stockDisponible,
                stockMinimo=inv.stockMinimo,
                estadoStock=estado,
            ))
        return data

    @staticmethod
    def kardex(db: Session, usuario_actual: Usuario, id_ubicacion: int | None = None, id_producto: int | None = None, desde: datetime | None = None, hasta: datetime | None = None, limite: int = 200) -> list[ReporteKardexResponse]:
        id_ubicacion = ReporteService._resolver_ubicacion(usuario_actual, id_ubicacion)
        stmt = (
            select(MovimientoInventario)
            .options(
                joinedload(MovimientoInventario.ubicacion),
                joinedload(MovimientoInventario.producto),
                joinedload(MovimientoInventario.usuario),
            )
            .order_by(MovimientoInventario.fechaHora.desc(), MovimientoInventario.idMovimiento.desc())
            .limit(limite)
        )
        if id_ubicacion is not None:
            stmt = stmt.where(MovimientoInventario.idUbicacion == id_ubicacion)
        if id_producto is not None:
            stmt = stmt.where(MovimientoInventario.idProducto == id_producto)
        if desde is not None:
            stmt = stmt.where(MovimientoInventario.fechaHora >= desde)
        if hasta is not None:
            stmt = stmt.where(MovimientoInventario.fechaHora <= hasta)

        return [
            ReporteKardexResponse(
                idMovimiento=mov.idMovimiento,
                fechaHora=mov.fechaHora,
                idUbicacion=mov.idUbicacion,
                ubicacion=mov.ubicacion.nombreUbicacion,
                idProducto=mov.idProducto,
                producto=mov.producto.nombreProducto,
                usuario=mov.usuario.correoElectronico,
                tipoMovimiento=mov.tipoMovimiento,
                motivoMovimiento=mov.motivoMovimiento,
                cantidad=mov.cantidad,
                tipoReferencia=mov.tipoReferencia,
                idReferencia=mov.idReferencia,
            )
            for mov in db.execute(stmt).scalars().all()
        ]

    @staticmethod
    def compras(db: Session, usuario_actual: Usuario, id_ubicacion: int | None = None, estado: str | None = None, desde: datetime | None = None, hasta: datetime | None = None, limite: int = 100) -> list[ReporteCompraResponse]:
        id_ubicacion = ReporteService._resolver_ubicacion(usuario_actual, id_ubicacion)
        stmt = (
            select(OrdenCompra)
            .options(
                joinedload(OrdenCompra.proveedor),
                joinedload(OrdenCompra.ubicacion_destino),
                joinedload(OrdenCompra.usuario_comprador),
                joinedload(OrdenCompra.usuario_receptor),
            )
            .order_by(OrdenCompra.fechaPedido.desc())
            .limit(limite)
        )
        if id_ubicacion is not None:
            stmt = stmt.where(OrdenCompra.idUbicacionDestino == id_ubicacion)
        if estado is not None:
            stmt = stmt.where(OrdenCompra.estado == estado)
        if desde is not None:
            stmt = stmt.where(OrdenCompra.fechaPedido >= desde)
        if hasta is not None:
            stmt = stmt.where(OrdenCompra.fechaPedido <= hasta)

        return [
            ReporteCompraResponse(
                idOrdenCompra=oc.idOrdenCompra,
                proveedor=oc.proveedor.razonSocial,
                ubicacionDestino=oc.ubicacion_destino.nombreUbicacion,
                usuarioComprador=oc.usuario_comprador.correoElectronico,
                usuarioReceptor=oc.usuario_receptor.correoElectronico if oc.usuario_receptor else None,
                fechaPedido=oc.fechaPedido,
                fechaRecepcion=oc.fechaRecepcion,
                estado=oc.estado,
                totalNeto=oc.totalNeto,
                totalIgv=oc.totalIgv,
                totalCompra=oc.totalCompra,
            )
            for oc in db.execute(stmt).unique().scalars().all()
        ]

    @staticmethod
    def reposiciones_por_estado(db: Session, usuario_actual: Usuario, id_ubicacion_destino: int | None = None) -> list[ReporteReposicionPorEstadoResponse]:
        id_ubicacion_destino = ReporteService._resolver_ubicacion(usuario_actual, id_ubicacion_destino)
        stmt = select(SolicitudReposicion.estado, func.count(SolicitudReposicion.idSolicitud)).group_by(SolicitudReposicion.estado)
        if id_ubicacion_destino is not None:
            stmt = stmt.where(SolicitudReposicion.idUbicacionDestino == id_ubicacion_destino)
        return [ReporteReposicionPorEstadoResponse(estado=fila[0], cantidad=fila[1]) for fila in db.execute(stmt).all()]
