class EstadoInvalidoError(Exception):
    """Transición de estado no permitida por la máquina de estados."""

    def __init__(self, mensaje: str = "Transición de estado inválida") -> None:
        super().__init__(mensaje)
