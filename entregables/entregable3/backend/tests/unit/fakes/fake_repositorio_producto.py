from app.application.ports.repositorio_producto import IRepositorioProducto
from app.domain.entities.producto import Producto
from typing import List, Optional

class FakeRepositorioProducto(IRepositorioProducto):
    def __init__(self, productos: List[Producto] = None):
        self._productos = productos or []

    def listar_por_sucursal(self, sucursal_id: int) -> List[Producto]:
        return [p for p in self._productos if p.sucursal_id == sucursal_id]

    def obtener_por_id(self, producto_id: int) -> Optional[Producto]:
        return next((p for p in self._productos if p.id == producto_id), None)

    def actualizar_stock(self, producto_id: int, nueva_cantidad: int) -> None:
        for p in self._productos:
            if p.id == producto_id:
                p.stock_actual = nueva_cantidad
                return