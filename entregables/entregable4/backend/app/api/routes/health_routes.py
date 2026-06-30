from fastapi import APIRouter
from sqlalchemy import text

from app.db.session import engine


router = APIRouter(
    prefix="/health",
    tags=["Health"]
)


@router.get("/db")
def verificar_base_datos():
    try:
        with engine.connect() as conexion:
            nombre_db = conexion.execute(text("SELECT DATABASE();")).scalar()

        return {
            "ok": True,
            "mensaje": "Conexión correcta a MySQL",
            "base_datos": nombre_db
        }

    except Exception as error:
        return {
            "ok": False,
            "mensaje": "Error de conexión a MySQL",
            "detalle": str(error)
        }