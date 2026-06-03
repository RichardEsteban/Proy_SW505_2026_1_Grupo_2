from app.domain.entities.producto import Producto
from app.application.ports.repositorio_producto import IRepositorioProducto
from typing import List

class VerificarStockMinimoUseCase:
    def __init__(self, repo: IRepositorioProducto):
        self.repo = repo

    def ejecutar(self, sucursal_id: int) -> List[Producto]:
        """Retorna lista de productos con stock bajo en la sucursal."""
        productos = self.repo.listar_por_sucursal(sucursal_id)
        return [p for p in productos if p.tiene_bajo_stock()]