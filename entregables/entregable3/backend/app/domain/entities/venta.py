from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional


@dataclass
class ItemVenta:
    producto_id: int
    cantidad: int
    precio_unitario: Decimal

    @property
    def subtotal(self) -> Decimal:
        return self.precio_unitario * self.cantidad


@dataclass
class Venta:
    id: Optional[int]
    vendedor_id: int
    sucursal_id: int
    items: List[ItemVenta]
    metodo_pago: str
    subtotal: Decimal = Decimal('0')
    igv: Decimal = Decimal('0')
    total: Decimal = Decimal('0')
    estado: str = 'completada'

    METODOS_PAGO_VALIDOS = {'efectivo', 'tarjeta', 'yape', 'plin'}