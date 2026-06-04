from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.venta import Venta


class IRepositorioVenta(ABC):

    @abstractmethod
    def guardar(self, venta: Venta) -> Venta:
        pass

    @abstractmethod
    def obtener_por_id(self, venta_id: int) -> Optional[Venta]:
        pass

    @abstractmethod
    def listar_por_vendedor(self, vendedor_id: int) -> List[Venta]:
        pass