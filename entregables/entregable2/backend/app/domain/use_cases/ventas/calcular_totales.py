from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass
from typing import List

IGV_TASA = Decimal('0.18')  # 18% Perú


@dataclass
class ItemCalculo:
    precio_unitario: Decimal
    cantidad: int


@dataclass
class ResultadoTotales:
    subtotal: Decimal
    igv: Decimal
    total: Decimal


class CalcularTotalesVentaUseCase:

    def ejecutar(self, items: List[ItemCalculo]) -> ResultadoTotales:
        subtotal = sum(
            (i.precio_unitario * i.cantidad for i in items),
            Decimal('0')
        )
        igv = (subtotal * IGV_TASA).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        total = subtotal + igv
        return ResultadoTotales(subtotal=subtotal, igv=igv, total=total)