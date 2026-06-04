from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.producto import Producto

class IRepositorioProducto(ABC):

    @abstractmethod
    def listar_por_sucursal(self, sucursal_id: int) -> List[Producto]:
        pass

    @abstractmethod
    def obtener_por_id(self, producto_id: int) -> Optional[Producto]:
        pass

    @abstractmethod
    def actualizar_stock(self, producto_id: int, nueva_cantidad: int) -> None:
        pass