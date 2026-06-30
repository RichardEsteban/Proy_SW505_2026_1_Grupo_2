from passlib.context import CryptContext


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def verificar_contrasena(contrasena_plana: str, contrasena_hash: str) -> bool:
    return pwd_context.verify(contrasena_plana, contrasena_hash)


def generar_hash_contrasena(contrasena: str) -> str:
    return pwd_context.hash(contrasena)