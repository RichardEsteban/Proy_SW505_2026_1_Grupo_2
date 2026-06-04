class StockInsuficiente(Exception):
    def __init__(self, producto_id: int, disponible: int, solicitado: int):
        super().__init__(
            f"Stock insuficiente para producto {producto_id}. "
            f"Disponible: {disponible}, Solicitado: {solicitado}"
        )
        self.producto_id = producto_id
        self.disponible = disponible
        self.solicitado = solicitado