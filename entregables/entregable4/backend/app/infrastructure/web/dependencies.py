"""Inyección de dependencias para los routers de FastAPI."""
from __future__ import annotations

from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.application.ports.repositorio_alerta import RepositorioAlerta
from app.application.ports.repositorio_producto import RepositorioProducto
from app.application.ports.repositorio_solicitud import RepositorioSolicitud
from app.application.ports.repositorio_usuario import RepositorioUsuario
from app.application.ports.repositorio_venta import RepositorioVenta
from app.domain.use_cases.accesos.autenticar_usuario import AutenticarUsuario
from app.domain.use_cases.accesos.cambiar_password import CambiarPassword
from app.domain.use_cases.accesos.inicializar_sistema import InicializarSistema
from app.domain.use_cases.accesos.recuperar_password import RecuperarPassword
from app.domain.use_cases.admin.gestionar_clientes import GestionarClientes
from app.domain.use_cases.admin.gestionar_productos import GestionarProductos
from app.domain.use_cases.admin.gestionar_proveedores import GestionarProveedores
from app.domain.use_cases.admin.gestionar_sucursales import GestionarSucursales
from app.domain.use_cases.admin.gestionar_usuarios import GestionarUsuarios
from app.domain.use_cases.almacen.registrar_compra import RegistrarCompra
from app.domain.use_cases.almacen.registrar_entrada import RegistrarEntrada
from app.domain.use_cases.inventario.consultar_disponibilidad import (
    ConsultarDisponibilidad,
)
from app.domain.use_cases.inventario.verificar_stock_minimo import VerificarStockMinimo
from app.domain.use_cases.reposicion.confirmar_recepcion import ConfirmarRecepcion
from app.domain.use_cases.reposicion.evaluar_solicitud import EvaluarSolicitud
from app.domain.use_cases.reposicion.generar_solicitud import GenerarSolicitud
from app.domain.use_cases.reposicion.registrar_envio import RegistrarEnvio
from app.domain.use_cases.reportes.generar_dashboard import GenerarDashboard
from app.domain.use_cases.reportes.generar_reporte_ventas import GenerarReporteVentas
from app.domain.use_cases.ventas.calcular_totales import CalcularTotales
from app.domain.use_cases.ventas.generar_comprobante import GenerarComprobante
from app.domain.use_cases.ventas.registrar_venta import RegistrarVenta
from app.infrastructure.config.settings import get_settings
from app.infrastructure.persistence.sqlalchemy.database import SessionLocal
from app.infrastructure.persistence.sqlalchemy.models import (
    AlmacenModel,
    ClienteModel,
    CompraModel,
    ProveedorModel,
    RolModel,
    SucursalModel,
)
from app.infrastructure.persistence.sqlalchemy.repositories import (
    SqlAlchemyAlertaRepository,
    SqlAlchemyProductoRepository,
    SqlAlchemySolicitudRepository,
    SqlAlchemyStockRepository,
    SqlAlchemyUsuarioRepository,
    SqlAlchemyVentaRepository,
)
from app.infrastructure.web.services.alerta_service import AlertaService
from app.infrastructure.web.services.email_service import EmailService
from app.infrastructure.web.services.generador_pdf import GeneradorPDFService
from app.infrastructure.web.services.jwt_service import jwt_service
from app.infrastructure.web.services.minio_service import MinioService


# --- DB session ---
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Repositorios ---
def get_repo_usuarios(db: Session = Depends(get_db)) -> RepositorioUsuario:
    return SqlAlchemyUsuarioRepository(db)


def get_repo_productos(db: Session = Depends(get_db)) -> RepositorioProducto:
    return SqlAlchemyProductoRepository(db)


def get_repo_ventas(db: Session = Depends(get_db)) -> RepositorioVenta:
    return SqlAlchemyVentaRepository(db)


def get_repo_solicitudes(db: Session = Depends(get_db)) -> RepositorioSolicitud:
    return SqlAlchemySolicitudRepository(db)


def get_repo_alertas(db: Session = Depends(get_db)) -> RepositorioAlerta:
    return SqlAlchemyAlertaRepository(db)


def get_repo_stock(db: Session = Depends(get_db)):
    return SqlAlchemyStockRepository(db)


# --- Servicios externos (singleton) ---
_settings_singleton = get_settings()
_email_service = EmailService(_settings_singleton)
_minio_service = MinioService(_settings_singleton)
_alerta_service = AlertaService()
_pdf_service = GeneradorPDFService(_minio_service)


def get_email_service() -> EmailService:
    return _email_service


def get_minio_service() -> MinioService:
    return _minio_service


def get_alerta_service() -> AlertaService:
    return _alerta_service


def get_pdf_service() -> GeneradorPDFService:
    return _pdf_service


# --- UoW helper ---
class _UnitOfWork:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repos_usuarios = SqlAlchemyUsuarioRepository(db)
        self.repos_productos = SqlAlchemyProductoRepository(db)
        self.repos_stock = SqlAlchemyStockRepository(db)
        self.repos_ventas = SqlAlchemyVentaRepository(db)
        self.repos_solicitudes = SqlAlchemySolicitudRepository(db)
        self.repos_alertas = SqlAlchemyAlertaRepository(db)
        self.repos_roles = _RolRepoShim(db)
        self.repos_sucursales = _SucursalRepoShim(db)
        self.repos_almacenes = _AlmacenRepoShim(db)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type:
            self.db.rollback()
        else:
            self.db.commit()

    def commit(self):
        self.db.commit()


def _uow(db: Session) -> _UnitOfWork:
    return _UnitOfWork(db)


# --- Shims de repos de catálogo (clases delgadas) ---

class _RolRepoShim:
    def __init__(self, db: Session) -> None:
        self.db = db

    def crear(self, nombre: str, descripcion: str, permisos: list):
        m = RolModel(
            nombre=nombre,
            descripcion=descripcion,
            permisos=str(permisos).replace("'", '"'),
        )
        self.db.add(m)
        self.db.flush()
        return m.id


class _SucursalRepoShim:
    def __init__(self, db: Session) -> None:
        self.db = db

    def listar(self):
        return self.db.execute(select(SucursalModel)).scalars().all()

    def crear(self, codigo, nombre, direccion):
        m = SucursalModel(codigo=codigo, nombre=nombre, direccion=direccion)
        self.db.add(m)
        self.db.flush()
        return m.id

    def actualizar(self, s):
        self.db.merge(s)
        self.db.flush()
        return s


class _AlmacenRepoShim:
    def __init__(self, db: Session) -> None:
        self.db = db

    def listar(self):
        return self.db.execute(select(AlmacenModel)).scalars().all()

    def crear(self, codigo, nombre, direccion, responsable_id=None):
        m = AlmacenModel(
            codigo=codigo,
            nombre=nombre,
            direccion=direccion,
            responsable_id=responsable_id,
        )
        self.db.add(m)
        self.db.flush()
        return m.id

    def actualizar(self, a):
        self.db.merge(a)
        self.db.flush()
        return a


class _ClienteRepoShim:
    def __init__(self, db: Session) -> None:
        self.db = db

    def listar(self):
        return self.db.execute(select(ClienteModel)).scalars().all()

    def buscar(self, termino="", limit=100):
        stmt = select(ClienteModel).limit(limit)
        if termino:
            like = f"%{termino}%"
            stmt = stmt.where(
                (ClienteModel.nombre.ilike(like))
                | (ClienteModel.numero_documento.ilike(like))
            )
        return self.db.execute(stmt).scalars().all()

    def obtener_por_id(self, cliente_id):
        return self.db.get(ClienteModel, cliente_id)

    def obtener_por_documento(self, tipo, numero):
        stmt = select(ClienteModel).where(
            ClienteModel.tipo_documento == tipo,
            ClienteModel.numero_documento == numero,
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def crear(self, c: ClienteModel):
        self.db.add(c)
        self.db.flush()
        return c

    def actualizar(self, c: ClienteModel):
        self.db.merge(c)
        self.db.flush()
        return c


class _ProveedorRepoShim:
    def __init__(self, db: Session) -> None:
        self.db = db

    def listar(self, solo_activos=True):
        stmt = select(ProveedorModel)
        if solo_activos:
            stmt = stmt.where(ProveedorModel.activo.is_(True))
        return self.db.execute(stmt).scalars().all()

    def obtener_por_id(self, pid):
        return self.db.get(ProveedorModel, pid)

    def obtener_por_ruc(self, ruc):
        stmt = select(ProveedorModel).where(ProveedorModel.ruc == ruc)
        return self.db.execute(stmt).scalar_one_or_none()

    def crear(self, p: ProveedorModel):
        self.db.add(p)
        self.db.flush()
        return p

    def actualizar(self, p: ProveedorModel):
        self.db.merge(p)
        self.db.flush()
        return p


class _CompraRepoShim:
    def __init__(self, db: Session) -> None:
        self.db = db

    def crear(self, data: dict):
        m = CompraModel(**data)
        self.db.add(m)
        self.db.flush()
        return m.id


class _ReporteServiceShim:
    """Implementación in-line del puerto GeneradorReporte."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def ventas(self, fecha_desde, fecha_hasta, sucursal_id=None):
        from app.infrastructure.persistence.sqlalchemy.models import VentaModel

        stmt = select(VentaModel).where(
            VentaModel.fecha >= fecha_desde, VentaModel.fecha <= fecha_hasta
        )
        if sucursal_id is not None:
            stmt = stmt.where(VentaModel.sucursal_id == sucursal_id)
        ventas = self.db.execute(stmt).scalars().all()
        return {
            "fecha_desde": fecha_desde.isoformat(),
            "fecha_hasta": fecha_hasta.isoformat(),
            "sucursal_id": sucursal_id,
            "cantidad_ventas": len(ventas),
            "subtotal": round(sum(v.subtotal for v in ventas), 2),
            "igv": round(sum(v.igv for v in ventas), 2),
            "total": round(sum(v.total for v in ventas), 2),
            "ticket_promedio": (
                round(sum(v.total for v in ventas) / len(ventas), 2) if ventas else 0
            ),
        }

    def inventario(self, sucursal_id=None):
        from app.infrastructure.persistence.sqlalchemy.models import StockModel

        stmt = select(StockModel)
        if sucurs_id := sucursal_id:
            stmt = stmt.where(StockModel.ubicacion_id == sucurs_id)
        stocks = self.db.execute(stmt).scalars().all()
        bajo_minimo = sum(1 for s in stocks if s.cantidad <= s.stock_minimo)
        return {
            "total_items": len(stocks),
            "items_bajo_minimo": bajo_minimo,
            "valor_total": 0,
        }

    def dashboard(self, sucursal_id=None):
        from datetime import datetime, timedelta

        hoy = datetime.utcnow().date()
        desde = datetime.combine(hoy - timedelta(days=30), datetime.min.time())
        hasta = datetime.utcnow()
        return {
            "kpi_ventas_30d": self.ventas(desde, hasta, sucursal_id),
            "kpi_inventario": self.inventario(sucursal_id),
            "alertas_activas": 0,
        }


# --- Casos de uso (inyectados) ---
def use_case_autenticar(db: Session = Depends(get_db)) -> AutenticarUsuario:
    return AutenticarUsuario(SqlAlchemyUsuarioRepository(db), jwt_service)


def use_case_cambiar_password(db: Session = Depends(get_db)) -> CambiarPassword:
    return CambiarPassword(SqlAlchemyUsuarioRepository(db), jwt_service)


def use_case_recuperar_password(db: Session = Depends(get_db)) -> RecuperarPassword:
    return RecuperarPassword(
        SqlAlchemyUsuarioRepository(db), _email_service, jwt_service
    )


def use_case_inicializar(db: Session = Depends(get_db)) -> InicializarSistema:
    return InicializarSistema(lambda: _uow(db), jwt_service)


def use_case_registrar_venta(db: Session = Depends(get_db)) -> RegistrarVenta:
    return RegistrarVenta(
        SqlAlchemyVentaRepository(db),
        SqlAlchemyProductoRepository(db),
        SqlAlchemyStockRepository(db),
        uow=lambda: _uow(db),
    )


def use_case_calcular_totales() -> CalcularTotales:
    return CalcularTotales(igv_porcentaje=get_settings().igv_porcentaje)


def use_case_generar_comprobante(db: Session = Depends(get_db)) -> GenerarComprobante:
    return GenerarComprobante(SqlAlchemyVentaRepository(db), _pdf_service)


def use_case_consultar_disponibilidad(
    db: Session = Depends(get_db),
) -> ConsultarDisponibilidad:
    return ConsultarDisponibilidad(
        SqlAlchemyStockRepository(db), SqlAlchemyProductoRepository(db)
    )


def use_case_verificar_stock_minimo(
    db: Session = Depends(get_db),
) -> VerificarStockMinimo:
    return VerificarStockMinimo(
        SqlAlchemyStockRepository(db),
        SqlAlchemyProductoRepository(db),
        SqlAlchemyAlertaRepository(db),
    )


def use_case_generar_solicitud(db: Session = Depends(get_db)) -> GenerarSolicitud:
    return GenerarSolicitud(
        SqlAlchemySolicitudRepository(db), SqlAlchemyStockRepository(db)
    )


def use_case_evaluar_solicitud(db: Session = Depends(get_db)) -> EvaluarSolicitud:
    return EvaluarSolicitud(SqlAlchemySolicitudRepository(db))


def use_case_registrar_envio(db: Session = Depends(get_db)) -> RegistrarEnvio:
    return RegistrarEnvio(SqlAlchemySolicitudRepository(db))


def use_case_confirmar_recepcion(db: Session = Depends(get_db)) -> ConfirmarRecepcion:
    return ConfirmarRecepcion(
        SqlAlchemySolicitudRepository(db), SqlAlchemyStockRepository(db)
    )


def use_case_registrar_entrada(db: Session = Depends(get_db)) -> RegistrarEntrada:
    return RegistrarEntrada(SqlAlchemyStockRepository(db), uow=lambda: _uow(db))


def use_case_registrar_compra(db: Session = Depends(get_db)) -> RegistrarCompra:
    return RegistrarCompra(
        SqlAlchemyStockRepository(db),
        _ProveedorRepoShim(db),
        _CompraRepoShim(db),
        uow=lambda: _uow(db),
    )


def use_case_gestionar_usuarios(
    db: Session = Depends(get_db),
) -> GestionarUsuarios:
    return GestionarUsuarios(SqlAlchemyUsuarioRepository(db), jwt_service)


def use_case_gestionar_productos(
    db: Session = Depends(get_db),
) -> GestionarProductos:
    return GestionarProductos(SqlAlchemyProductoRepository(db))


def use_case_gestionar_sucursales(
    db: Session = Depends(get_db),
) -> GestionarSucursales:
    return GestionarSucursales(_SucursalRepoShim(db), _AlmacenRepoShim(db))


def use_case_gestionar_clientes(db: Session = Depends(get_db)) -> GestionarClientes:
    return GestionarClientes(_ClienteRepoShim(db))


def use_case_gestionar_proveedores(
    db: Session = Depends(get_db),
) -> GestionarProveedores:
    return GestionarProveedores(_ProveedorRepoShim(db))


def use_case_reporte_ventas(db: Session = Depends(get_db)) -> GenerarReporteVentas:
    return GenerarReporteVentas(_ReporteServiceShim(db))


def use_case_dashboard(db: Session = Depends(get_db)) -> GenerarDashboard:
    return GenerarDashboard(_ReporteServiceShim(db))


# --- Auth dependency ---
bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> dict:
    """Decodifica el JWT y devuelve los claims."""
    try:
        payload = jwt_service.verificar_token(credentials.credentials)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if payload.get("scope") == "reset":
        raise HTTPException(status_code=401, detail="Token no válido para API")
    return payload


def require_role(*roles_permitidos: str):
    """Factory que crea un dependency que valida el rol del usuario."""
    def dep(user: dict = Depends(get_current_user)) -> dict:
        if user.get("rol") not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para realizar esta acción",
            )
        return user
    return dep
