import pytest
from decimal import Decimal
from app.domain.entities.venta import ItemVenta
from app.domain.entities.producto import Producto
from app.domain.exceptions.stock_insuficiente import StockInsuficiente
from app.domain.use_cases.ventas.registrar_venta import RegistrarVentaUseCase
from tests.unit.fakes.fake_repositorio_venta import FakeRepositorioVenta
from tests.unit.fakes.fake_repositorio_producto import FakeRepositorioProducto


def _crear_producto(id: int, stock_actual: int, stock_minimo: int = 5):
    return Producto(
        id=id,
        codigo=f'P{id:03d}',
        nombre=f'Producto {id}',
        precio=Decimal('50.00'),
        stock_actual=stock_actual,
        stock_minimo=stock_minimo,
        sucursal_id=1
    )


class TestRegistrarVenta:

    def setup_method(self):
        self.producto = _crear_producto(id=1, stock_actual=10)
        self.fake_repo_producto = FakeRepositorioProducto([self.producto])
        self.fake_repo_venta = FakeRepositorioVenta()
        self.use_case = RegistrarVentaUseCase(
            repo_venta=self.fake_repo_venta,
            repo_producto=self.fake_repo_producto
        )

    # PU-V03
    def test_venta_stock_insuficiente(self):
        items = [ItemVenta(producto_id=1, cantidad=20, precio_unitario=Decimal('50.00'))]

        with pytest.raises(StockInsuficiente):
            self.use_case.ejecutar(
                vendedor_id=1,
                sucursal_id=1,
                items=items,
                metodo_pago='efectivo'
            )
    
    # PU-V04
    def test_venta_exitosa_descuenta_stock(self):
        items = [ItemVenta(producto_id=1, cantidad=3, precio_unitario=Decimal('50.00'))]

        self.use_case.ejecutar(
            vendedor_id=1,
            sucursal_id=1,
            items=items,
            metodo_pago='efectivo'
        )

        producto_actualizado = self.fake_repo_producto.obtener_por_id(1)
        assert producto_actualizado.stock_actual == 7  # 10 - 3

    # PU-V05
    def test_venta_metodo_pago_invalido(self):
        items = [ItemVenta(producto_id=1, cantidad=1, precio_unitario=Decimal('50.00'))]

        with pytest.raises(ValueError):
            self.use_case.ejecutar(
                vendedor_id=1,
                sucursal_id=1,
                items=items,
                metodo_pago='bitcoin'
            )

    # Test extra 
    def test_venta_exitosa_se_persiste(self):
        items = [ItemVenta(producto_id=1, cantidad=2, precio_unitario=Decimal('50.00'))]

        venta = self.use_case.ejecutar(
            vendedor_id=1,
            sucursal_id=1,
            items=items,
            metodo_pago='yape'
        )

        assert venta.id is not None
        assert venta.total == Decimal('118.00')
        assert venta.igv == Decimal('18.00')