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