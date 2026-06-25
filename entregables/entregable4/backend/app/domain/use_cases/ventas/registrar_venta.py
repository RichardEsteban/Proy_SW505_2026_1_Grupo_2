"""Caso de uso: Registrar una venta (POS)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List

from app.application.ports.repositorio_producto import RepositorioProducto
from app.application.ports.repositorio_venta import RepositorioVenta
from app.domain.entities.stock import Stock, TipoUbicacion
from app.domain.entities.venta import DetalleVenta, TipoComprobante, Venta
from app.domain.exceptions.stock_insuficiente import StockInsuficienteError


@dataclass
class ItemVentaInput:
    producto_id: int
    cantidad: float
    precio_unitario: float
    descuento: float = 0.0


@dataclass
class VentaInput:
    serie: str
    numero: str
    tipo_comprobante: TipoComprobante
    sucursal_id: int
    usuario_id: int
    cliente_id: int | None
    items: List[ItemVentaInput]
    igv_porcentaje: float = 18.0


class RegistrarVenta:
    def __init__(
        self,
        repo_ventas: RepositorioVenta,
        repo_productos: RepositorioProducto,
        repo_stock,
        uow=None,
    ) -> None:
        self._ventas = repo_ventas
        self._productos = repo_productos
        self._stock = repo_stock
        self._uow = uow

    def ejecutar(self, data: VentaInput) -> Venta:
        with self._uow() as uow:
            # 1) Verificar stock y armar detalles
            detalles: List[DetalleVenta] = []
            for item in data.items:
                producto = self._productos.obtener_por_id(item.producto_id)
                if producto is None:
                    raise ValueError(f"Producto {item.producto_id} no existe")

                stock = self._stock.obtener(
                    producto_id=item.producto_id,
                    ubicacion_tipo=TipoUbicacion.SUCURSAL,
                    ubicacion_id=data.sucursal_id,
                )
                if stock is None or stock.cantidad < item.cantidad:
                    disponible = stock.cantidad if stock else 0.0
                    raise StockInsuficienteError(
                        producto_id=item.producto_id,
                        disponible=disponible,
                        requerido=item.cantidad,
                    )

                det = DetalleVenta(
                    id=None,
                    venta_id=None,
                    producto_id=item.producto_id,
                    cantidad=item.cantidad,
                    precio_unitario=item.precio_unitario,
                    descuento=item.descuento,
                )
                det.calcular(data.igv_porcentaje)
                detalles.append(det)

            # 2) Construir venta
            venta = Venta(
                id=None,
                serie=data.serie,
                numero=data.numero,
                tipo_comprobante=data.tipo_comprobante,
                sucursal_id=data.sucursal_id,
                cliente_id=data.cliente_id,
                usuario_id=data.usuario_id,
                fecha=datetime.utcnow(),
                detalles=detalles,
            )
            venta.calcular_totales(data.igv_porcentaje)

            # 3) Persistir venta y descontar stock
            venta_creada = self._ventas.crear(venta)
            for d in venta_creada.detalles:
                stock.descontar(d.cantidad)
                self._stock.actualizar(stock)
            uow.commit()
            return venta_creada
