import pytest
from decimal import Decimal
from app.domain.use_cases.ventas.calcular_totales import (
    CalcularTotalesVentaUseCase, ItemCalculo
)


class TestCalcularTotalesVenta:

    def setup_method(self):
        self.use_case = CalcularTotalesVentaUseCase()

    # PU-V01
    def test_calculo_igv_exacto(self):
        items = [ItemCalculo(precio_unitario=Decimal('100.00'), cantidad=1)]
        resultado = self.use_case.ejecutar(items)

        assert resultado.subtotal == Decimal('100.00')
        assert resultado.igv == Decimal('18.00')
        assert resultado.total == Decimal('118.00')

     # PU-V02
    def test_calculo_multiples_items(self):
        items = [
            ItemCalculo(precio_unitario=Decimal('50.00'), cantidad=2),
            ItemCalculo(precio_unitario=Decimal('30.00'), cantidad=1),
        ]
        resultado = self.use_case.ejecutar(items)

        assert resultado.subtotal == Decimal('130.00')
        assert resultado.igv == Decimal('23.40')
        assert resultado.total == Decimal('153.40')   
    
    # PU-V06
    def test_igv_cero_si_subtotal_cero(self):
        resultado = self.use_case.ejecutar([])

        assert resultado.subtotal == Decimal('0')
        assert resultado.igv == Decimal('0.00')
        assert resultado.total == Decimal('0')