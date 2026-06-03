import pytest
from decimal import Decimal
from app.domain.entities.producto import Producto
from app.domain.use_cases.inventario.verificar_stock_minimo import VerificarStockMinimoUseCase
from tests.unit.fakes.fake_repositorio_producto import FakeRepositorioProducto


def _crear_producto(id, stock_actual, stock_minimo):
    return Producto(
        id=id, codigo=f'P{id:03d}', nombre=f'Producto {id}',
        precio=Decimal('10.00'), stock_actual=stock_actual,
        stock_minimo=stock_minimo, sucursal_id=1
    )


class TestVerificarStockMinimo:

    # PU-I01: BVA on-point — stock == mínimo, NO debe dar alerta
    def test_stock_igual_minimo_no_alerta(self):
        producto = _crear_producto(1, stock_actual=10, stock_minimo=10)
        use_case = VerificarStockMinimoUseCase(FakeRepositorioProducto([producto]))
        resultado = use_case.ejecutar(sucursal_id=1)
        assert len(resultado) == 0  # False = sin alerta

    # PU-I02: BVA off-point — stock = mínimo - 1, SÍ debe dar alerta
    def test_stock_un_menos_minimo_alerta(self):
        producto = _crear_producto(1, stock_actual=9, stock_minimo=10)
        use_case = VerificarStockMinimoUseCase(FakeRepositorioProducto([producto]))
        resultado = use_case.ejecutar(sucursal_id=1)
        assert len(resultado) == 1  # True = alerta

    # PU-I03: BVA extremo — stock = 0, siempre alerta
    def test_stock_cero_alerta(self):
        producto = _crear_producto(1, stock_actual=0, stock_minimo=10)
        use_case = VerificarStockMinimoUseCase(FakeRepositorioProducto([producto]))
        resultado = use_case.ejecutar(sucursal_id=1)
        assert len(resultado) == 1

    # PU-I04: BVA extremo — stock muy alto, sin alerta
    def test_stock_mayor_minimo_no_alerta(self):
        producto = _crear_producto(1, stock_actual=20, stock_minimo=10)
        use_case = VerificarStockMinimoUseCase(FakeRepositorioProducto([producto]))
        resultado = use_case.ejecutar(sucursal_id=1)
        assert len(resultado) == 0

    # PU-I05: Partición equivalente — lista con 3 productos, 2 bajo stock
    def test_lista_productos_bajo_stock(self):
        productos = [
            _crear_producto(1, stock_actual=5, stock_minimo=10),   # bajo
            _crear_producto(2, stock_actual=15, stock_minimo=10),  # ok
            _crear_producto(3, stock_actual=2, stock_minimo=10),   # bajo
        ]
        use_case = VerificarStockMinimoUseCase(FakeRepositorioProducto(productos))
        resultado = use_case.ejecutar(sucursal_id=1)
        assert len(resultado) == 2
        assert resultado[0].id == 1
        assert resultado[1].id == 3

    # PU-I06: Caso borde — lista vacía
    def test_lista_vacia_sin_alertas(self):
        use_case = VerificarStockMinimoUseCase(FakeRepositorioProducto([]))
        resultado = use_case.ejecutar(sucursal_id=1)
        assert resultado == []