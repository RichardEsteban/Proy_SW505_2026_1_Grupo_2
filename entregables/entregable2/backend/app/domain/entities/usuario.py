from dataclasses import dataclass

@dataclass
class Usuario:
    id: int
    email: str
    password_hash: str
    rol: str
    activo: bool = True
    requiere_cambio_pass: bool = False
