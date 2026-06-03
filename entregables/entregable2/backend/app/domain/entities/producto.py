from dataclasses import dataclass
from decimal import Decimal

@dataclass
class Producto:
    id: int
    codigo: str
    nombre: str
    precio: Decimal
    stock_actual: int
    stock_minimo: int
    sucursal_id: int
    activo: bool = True

    def tiene_bajo_stock(self) -> bool:
        """Retorna True si el stock está por DEBAJO del mínimo."""
        return self.stock_actual < self.stock_minimo

    def tiene_stock_suficiente(self, cantidad: int) -> bool:
        """Retorna True si hay suficiente stock para la cantidad pedida."""
        return self.stock_actual >= cantidad