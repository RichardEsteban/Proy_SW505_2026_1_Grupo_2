from app.domain.entities.venta import Venta, ItemVenta
from app.domain.exceptions.stock_insuficiente import StockInsuficiente
from app.application.ports.repositorio_venta import IRepositorioVenta
from app.application.ports.repositorio_producto import IRepositorioProducto
from app.domain.use_cases.ventas.calcular_totales import (
    CalcularTotalesVentaUseCase, ItemCalculo
)
from typing import List


class RegistrarVentaUseCase:

    def __init__(
        self,
        repo_venta: IRepositorioVenta,
        repo_producto: IRepositorioProducto
    ):
        self.repo_venta = repo_venta
        self.repo_producto = repo_producto
        self.calcular_totales = CalcularTotalesVentaUseCase()

    def ejecutar(
        self,
        vendedor_id: int,
        sucursal_id: int,
        items: List[ItemVenta],
        metodo_pago: str
    ) -> Venta:
        # Validar método de pago
        if metodo_pago not in Venta.METODOS_PAGO_VALIDOS:
            raise ValueError(
                f"Método de pago inválido: '{metodo_pago}'. "
                f"Válidos: {Venta.METODOS_PAGO_VALIDOS}"
            )

        # Validar stock por cada item
        for item in items:
            producto = self.repo_producto.obtener_por_id(item.producto_id)
            if not producto.tiene_stock_suficiente(item.cantidad):
                raise StockInsuficiente(
                    producto_id=item.producto_id,
                    stock_disponible=producto.stock_actual,
                    cantidad_pedida=item.cantidad
                )

        # Calcular totales con IGV
        items_calculo = [
            ItemCalculo(precio_unitario=i.precio_unitario, cantidad=i.cantidad)
            for i in items
        ]
        totales = self.calcular_totales.ejecutar(items_calculo)

        # Descontar stock
        for item in items:
            producto = self.repo_producto.obtener_por_id(item.producto_id)
            self.repo_producto.actualizar_stock(
                item.producto_id,
                producto.stock_actual - item.cantidad
            )

        # Persistir venta
        venta = Venta(
            id=None,
            vendedor_id=vendedor_id,
            sucursal_id=sucursal_id,
            items=items,
            metodo_pago=metodo_pago,
            subtotal=totales.subtotal,
            igv=totales.igv,
            total=totales.total
        )
        return self.repo_venta.guardar(venta)