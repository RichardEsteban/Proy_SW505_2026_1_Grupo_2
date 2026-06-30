from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.empresa import Empresa
from app.models.rol import Rol
from app.models.ubicacion import Ubicacion
from app.models.usuario import Usuario
from app.utils.password import generar_hash_contrasena


def init_db():
    print("🚀 INIT_DB SE ESTA EJECUTANDO")
    db: Session = SessionLocal()

    try:
        empresa = db.query(Empresa).first()

        if not empresa:
            empresa = Empresa(
                nombreEmpresa="Empresa Demo",
                isInicializado=True,
                timer_revision_minutos=60,
                igv_porcentaje=18.00,
                moneda="PEN"
            )
            db.add(empresa)
            db.flush()

        roles_base = [
            "ADMIN",
            "VENDEDOR",
            "SUPERVISOR_SUCURSAL",
            "SUPERVISOR_ALMACEN"
        ]

        for nombre_rol in roles_base:
            rol_existente = db.query(Rol).filter(
                Rol.nombreRol == nombre_rol
            ).first()

            if not rol_existente:
                db.add(Rol(nombreRol=nombre_rol))

        db.flush()

        ubicacion = db.query(Ubicacion).first()

        if not ubicacion:
            ubicacion = Ubicacion(
                idEmpresa=empresa.idEmpresa,
                nombreUbicacion="Almacén Central",
                tipoUbicacion="ALMACEN",
                direccion="Dirección demo",
                isActivo=True
            )
            db.add(ubicacion)
            db.flush()

        rol_admin = db.query(Rol).filter(
            Rol.nombreRol == "ADMIN"
        ).first()

        admin = db.query(Usuario).filter(
            Usuario.correoElectronico == "admin@demo.com"
        ).first()

        if not admin:
            admin = Usuario(
                idUbicacion=ubicacion.idUbicacion,
                idRol=rol_admin.idRol,
                correoElectronico="admin@demo.com",
                contrasenaHash=generar_hash_contrasena("Admin123*"),
                isActivo=True,
                isContrasenaTemporal=True
            )
            db.add(admin)

        db.commit()

        print("Datos iniciales creados correctamente.")
        print("Correo: admin@demo.com")
        print("Contraseña: Admin123*")

    except Exception as error:
        db.rollback()
        print("Error inicializando la base de datos:", error)

    finally:
        db.close()


if __name__ == "__main__":
    init_db()