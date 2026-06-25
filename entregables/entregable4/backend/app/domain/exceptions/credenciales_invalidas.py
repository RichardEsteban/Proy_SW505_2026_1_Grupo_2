class CredencialesInvalidasError(Exception):
    """Usuario/contraseña incorrectos o cuenta bloqueada/inactiva."""

    def __init__(self, mensaje: str = "Credenciales inválidas") -> None:
        super().__init__(mensaje)
