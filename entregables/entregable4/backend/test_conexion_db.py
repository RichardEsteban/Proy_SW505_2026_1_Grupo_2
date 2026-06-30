from sqlalchemy import text

from app.db.session import engine


def probar_conexion():
    try:
        with engine.connect() as conexion:
            resultado = conexion.execute(text("SELECT DATABASE();"))
            nombre_db = resultado.scalar()

            print("Conexión correcta a MySQL.")
            print(f"Base de datos conectada: {nombre_db}")

    except Exception as error:
        print("Error de conexión a MySQL:")
        print(error)


if __name__ == "__main__":
    probar_conexion()