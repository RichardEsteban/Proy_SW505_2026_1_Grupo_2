"""Tests del cálculo de IGV (lógica de dominio)."""
import pytest

from app.domain.use_cases.ventas.calcular_totales import (
    CalcularTotales,
    ItemCalculo,
)


def test_calculo_basico():
    uc = CalcularTotales(igv_porcentaje=18.0)
    r = uc.ejecutar(
        [
            ItemCalculo(cantidad=2, precio_unitario=118, descuento=0),
        ]
    )
    # 2 * 118 = 236 total, igv=36, subtotal=200
    assert r.subtotal == 200.0
    assert r.igv == 36.0
    assert r.total == 236.0


def test_calculo_con_descuento():
    uc = CalcularTotales(igv_porcentaje=18.0)
    r = uc.ejecutar(
        [ItemCalculo(cantidad=1, precio_unitario=100, descuento=10)]
    )
    # bruto = 100 - 10 = 90, igv=13.73, subtotal=76.27, total=90
    assert r.total == 90.0
    assert round(r.subtotal, 2) == 76.27
    assert round(r.igv, 2) == 13.73


def test_items_multiples():
    uc = CalcularTotales(igv_porcentaje=18.0)
    r = uc.ejecutar(
        [
            ItemCalculo(cantidad=1, precio_unitario=100),
            ItemCalculo(cantidad=2, precio_unitario=50),
        ]
    )
    assert r.total == 200.0
    assert len(r.detalle) == 2
