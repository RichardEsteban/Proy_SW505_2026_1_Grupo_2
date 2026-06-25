class StockInsuficienteError(Exception):
    """Se lanza cuando se intenta vender/mover más unidades de las disponibles."""

    def __init__(
        self,
        producto_id: int,
        disponible: float,
        requerido: float,
    ) -> None:
        self.producto_id = producto_id
        self.disponible = disponible
        self.requerido = requerido
        super().__init__(
            f"Stock insuficiente del producto {producto_id}: "
            f"disponible={disponible}, requerido={requerido}"
        )
