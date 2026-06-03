from app.application.ports.repositorio_venta import IRepositorioVenta
from app.domain.entities.venta import Venta
from typing import List, Optional


class FakeRepositorioVenta(IRepositorioVenta):

    def __init__(self):
        self._ventas: List[Venta] = []
        self._next_id = 1

    def guardar(self, venta: Venta) -> Venta:
        venta.id = self._next_id
        self._next_id += 1
        self._ventas.append(venta)
        return venta

    def obtener_por_id(self, venta_id: int) -> Optional[Venta]:
        return next((v for v in self._ventas if v.id == venta_id), None)

    def listar_por_vendedor(self, vendedor_id: int) -> List[Venta]:
        return [v for v in self._ventas if v.vendedor_id == vendedor_id]