from app.domain.entities.producto import Producto
from app.application.ports.repositorio_producto import IRepositorioProducto
from typing import List

class ObtenerProductosBajoStockUseCase:
    def __init__(self, repo: IRepositorioProducto):
        self.repo = repo

    def ejecutar(self, sucursal_id: int) -> List[Producto]:
        productos = self.repo.listar_por_sucursal(sucursal_id)
        return [p for p in productos if p.tiene_bajo_stock()]