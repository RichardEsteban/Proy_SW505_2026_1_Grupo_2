"""Implementaciones SQLAlchemy de los puertos (repositorios).

Cada repositorio se encarga de traducir entre el modelo ORM y la entidad
de dominio, preservando la independencia del dominio.
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.orm import Session, selectinload

from app.application.ports.repositorio_alerta import RepositorioAlerta
from app.application.ports.repositorio_producto import RepositorioProducto
from app.application.ports.repositorio_solicitud import RepositorioSolicitud
from app.application.ports.repositorio_usuario import RepositorioUsuario
from app.application.ports.repositorio_venta import RepositorioVenta
from app.domain.entities.alerta import Alerta, EstadoAlerta, TipoAlerta
from app.domain.entities.producto import Producto
from app.domain.entities.solicitud import (
    DetalleSolicitud,
    EstadoSolicitud,
    SolicitudReposicion,
)
from app.domain.entities.stock import Stock, TipoUbicacion
from app.domain.entities.usuario import EstadoUsuario, Usuario
from app.domain.entities.venta import DetalleVenta, EstadoVenta, TipoComprobante, Venta
from app.infrastructure.persistence.sqlalchemy.models import (
    AlertaModel,
    DetalleSolicitudModel,
    DetalleVentaModel,
    ProductoModel,
    SolicitudModel,
    StockModel,
    UsuarioModel,
    VentaModel,
)


# ---------- Mappers ----------

def _usuario_to_domain(m: UsuarioModel) -> Usuario:
    return Usuario(
        id=m.id,
        dni=m.dni,
        nombre=m.nombre,
        apellido=m.apellido,
        email=m.email,
        username=m.username,
        password_hash=m.password_hash,
        rol_id=m.rol_id,
        sucursal_id=m.sucursal_id,
        estado=EstadoUsuario(m.estado),
        debe_cambiar_password=m.debe_cambiar_password,
        ultimo_acceso=m.ultimo_acceso,
        intentos_fallidos=m.intentos_fallidos,
        created_at=m.created_at,
        updated_at=m.updated_at,
        deleted_at=m.deleted_at,
    )


def _producto_to_domain(m: ProductoModel) -> Producto:
    return Producto(
        id=m.id,
        sku=m.sku,
        codigo_barra=m.codigo_barra,
        nombre=m.nombre,
        descripcion=m.descripcion,
        categoria_id=m.categoria_id,
        proveedor_id=m.proveedor_id,
        precio_compra=m.precio_compra,
        precio_venta=m.precio_venta,
        incluye_igv=m.incluye_igv,
        unidad_medida=m.unidad_medida,
        imagen_url=m.imagen_url,
        activo=m.activo,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


def _stock_to_domain(m: StockModel) -> Stock:
    return Stock(
        id=m.id,
        producto_id=m.producto_id,
        ubicacion_tipo=TipoUbicacion(m.ubicacion_tipo),
        ubicacion_id=m.ubicacion_id,
        cantidad=m.cantidad,
        stock_minimo=m.stock_minimo,
        stock_maximo=m.stock_maximo,
        updated_at=m.updated_at,
    )


def _alerta_to_domain(m: AlertaModel) -> Alerta:
    return Alerta(
        id=m.id,
        tipo=TipoAlerta(m.tipo),
        producto_id=m.producto_id,
        ubicacion_tipo=m.ubicacion_tipo,
        ubicacion_id=m.ubicacion_id,
        cantidad_actual=m.cantidad_actual,
        stock_referencia=m.stock_referencia,
        estado=EstadoAlerta(m.estado),
        mensaje=m.mensaje,
        created_at=m.created_at,
        atendida_at=m.atendida_at,
    )


def _solicitud_to_domain(
    m: SolicitudModel, detalles: List[DetalleSolicitudModel]
) -> SolicitudReposicion:
    return SolicitudReposicion(
        id=m.id,
        codigo=m.codigo,
        sucursal_origen_id=m.sucursal_origen_id,
        almacen_destino_id=m.almacen_destino_id,
        usuario_solicita_id=m.usuario_solicita_id,
        usuario_evalua_id=m.usuario_evalua_id,
        estado=EstadoSolicitud(m.estado),
        motivo=m.motivo,
        observacion=m.observacion,
        fecha_solicitud=m.fecha_solicitud,
        fecha_evaluacion=m.fecha_evaluacion,
        fecha_envio=m.fecha_envio,
        fecha_recepcion=m.fecha_recepcion,
        detalles=[
            DetalleSolicitud(
                id=d.id,
                solicitud_id=d.solicitud_id,
                producto_id=d.producto_id,
                cantidad_solicitada=d.cantidad_solicitada,
                cantidad_enviada=d.cantidad_enviada,
                cantidad_recibida=d.cantidad_recibida,
            )
            for d in detalles
        ],
    )


def _venta_to_domain(
    m: VentaModel, detalles: List[DetalleVentaModel]
) -> Venta:
    return Venta(
        id=m.id,
        serie=m.serie,
        numero=m.numero,
        tipo_comprobante=TipoComprobante(m.tipo_comprobante),
        sucursal_id=m.sucursal_id,
        cliente_id=m.cliente_id,
        usuario_id=m.usuario_id,
        fecha=m.fecha,
        subtotal=m.subtotal,
        igv=m.igv,
        descuento_total=m.descuento_total,
        total=m.total,
        estado=EstadoVenta(m.estado),
        pdf_url=m.pdf_url,
        created_at=m.created_at,
        detalles=[
            DetalleVenta(
                id=d.id,
                venta_id=d.venta_id,
                producto_id=d.producto_id,
                cantidad=d.cantidad,
                precio_unitario=d.precio_unitario,
                descuento=d.descuento,
                igv=d.igv,
                subtotal=d.subtotal,
                total=d.total,
            )
            for d in detalles
        ],
    )


# ---------- Repositorio Usuario ----------

class SqlAlchemyUsuarioRepository(RepositorioUsuario):
    def __init__(self, db: Session) -> None:
        self.db = db

    def obtener_por_id(self, usuario_id: int) -> Optional[Usuario]:
        m = self.db.get(UsuarioModel, usuario_id)
        return _usuario_to_domain(m) if m else None

    def obtener_por_username(self, username: str) -> Optional[Usuario]:
        stmt = select(UsuarioModel).where(UsuarioModel.username == username)
        m = self.db.execute(stmt).scalar_one_or_none()
        return _usuario_to_domain(m) if m else None

    def obtener_por_dni(self, dni: str) -> Optional[Usuario]:
        stmt = select(UsuarioModel).where(UsuarioModel.dni == dni)
        m = self.db.execute(stmt).scalar_one_or_none()
        return _usuario_to_domain(m) if m else None

    def listar(self, sucursal_id: Optional[int] = None) -> List[Usuario]:
        stmt = select(UsuarioModel).where(UsuarioModel.deleted_at.is_(None))
        if sucursal_id is not None:
            stmt = stmt.where(UsuarioModel.sucursal_id == sucursal_id)
        return [_usuario_to_domain(m) for m in self.db.execute(stmt).scalars()]

    def crear(self, usuario: Usuario) -> Usuario:
        m = UsuarioModel(
            dni=usuario.dni,
            nombre=usuario.nombre,
            apellido=usuario.apellido,
            email=usuario.email,
            username=usuario.username,
            password_hash=usuario.password_hash,
            rol_id=usuario.rol_id,
            sucursal_id=usuario.sucursal_id,
            estado=usuario.estado.value,
            debe_cambiar_password=usuario.debe_cambiar_password,
        )
        self.db.add(m)
        self.db.flush()
        return _usuario_to_domain(m)

    def actualizar(self, usuario: Usuario) -> Usuario:
        m = self.db.get(UsuarioModel, usuario.id)
        if not m:
            raise ValueError(f"Usuario {usuario.id} no existe")
        m.nombre = usuario.nombre
        m.apellido = usuario.apellido
        m.email = usuario.email
        m.username = usuario.username
        m.password_hash = usuario.password_hash
        m.rol_id = usuario.rol_id
        m.sucursal_id = usuario.sucursal_id
        m.estado = usuario.estado.value
        m.debe_cambiar_password = usuario.debe_cambiar_password
        m.ultimo_acceso = usuario.ultimo_acceso
        m.intentos_fallidos = usuario.intentos_fallidos
        self.db.flush()
        return _usuario_to_domain(m)

    def eliminar(self, usuario_id: int) -> None:
        m = self.db.get(UsuarioModel, usuario_id)
        if m:
            m.deleted_at = datetime.utcnow()
            self.db.flush()


# ---------- Repositorio Producto ----------

class SqlAlchemyProductoRepository(RepositorioProducto):
    def __init__(self, db: Session) -> None:
        self.db = db

    def obtener_por_id(self, producto_id: int) -> Optional[Producto]:
        m = self.db.get(ProductoModel, producto_id)
        return _producto_to_domain(m) if m else None

    def obtener_por_sku(self, sku: str) -> Optional[Producto]:
        stmt = select(ProductoModel).where(ProductoModel.sku == sku)
        m = self.db.execute(stmt).scalar_one_or_none()
        return _producto_to_domain(m) if m else None

    def obtener_por_codigo_barra(self, codigo: str) -> Optional[Producto]:
        stmt = select(ProductoModel).where(ProductoModel.codigo_barra == codigo)
        m = self.db.execute(stmt).scalar_one_or_none()
        return _producto_to_domain(m) if m else None

    def buscar(
        self, termino: str = "", categoria_id: Optional[int] = None, limit: int = 50
    ) -> List[Producto]:
        stmt = select(ProductoModel).where(ProductoModel.activo.is_(True)).limit(limit)
        if termino:
            like = f"%{termino}%"
            stmt = stmt.where(
                (ProductoModel.nombre.ilike(like)) | (ProductoModel.sku.ilike(like))
            )
        if categoria_id is not None:
            stmt = stmt.where(ProductoModel.categoria_id == categoria_id)
        return [_producto_to_domain(m) for m in self.db.execute(stmt).scalars()]

    def listar(self, solo_activos: bool = True) -> List[Producto]:
        stmt = select(ProductoModel)
        if solo_activos:
            stmt = stmt.where(ProductoModel.activo.is_(True))
        return [_producto_to_domain(m) for m in self.db.execute(stmt).scalars()]

    def crear(self, producto: Producto) -> Producto:
        m = ProductoModel(
            sku=producto.sku,
            codigo_barra=producto.codigo_barra,
            nombre=producto.nombre,
            descripcion=producto.descripcion,
            categoria_id=producto.categoria_id,
            proveedor_id=producto.proveedor_id,
            precio_compra=producto.precio_compra,
            precio_venta=producto.precio_venta,
            incluye_igv=producto.incluye_igv,
            unidad_medida=producto.unidad_medida,
            imagen_url=producto.imagen_url,
            activo=producto.activo,
        )
        self.db.add(m)
        self.db.flush()
        return _producto_to_domain(m)

    def actualizar(self, producto: Producto) -> Producto:
        m = self.db.get(ProductoModel, producto.id)
        if not m:
            raise ValueError(f"Producto {producto.id} no existe")
        m.nombre = producto.nombre
        m.descripcion = producto.descripcion
        m.categoria_id = producto.categoria_id
        m.proveedor_id = producto.proveedor_id
        m.precio_compra = producto.precio_compra
        m.precio_venta = producto.precio_venta
        m.incluye_igv = producto.incluye_igv
        m.unidad_medida = producto.unidad_medida
        m.imagen_url = producto.imagen_url
        m.activo = producto.activo
        self.db.flush()
        return _producto_to_domain(m)

    def eliminar(self, producto_id: int) -> None:
        m = self.db.get(ProductoModel, producto_id)
        if m:
            m.activo = False
            self.db.flush()


# ---------- Repositorio Stock (helper) ----------

class SqlAlchemyStockRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def obtener(
        self, producto_id: int, ubicacion_tipo: TipoUbicacion, ubicacion_id: int
    ) -> Optional[Stock]:
        stmt = select(StockModel).where(
            and_(
                StockModel.producto_id == producto_id,
                StockModel.ubicacion_tipo == ubicacion_tipo.value,
                StockModel.ubicacion_id == ubicacion_id,
            )
        )
        m = self.db.execute(stmt).scalar_one_or_none()
        return _stock_to_domain(m) if m else None

    def listar(
        self,
        ubicacion_tipo: Optional[TipoUbicacion] = None,
        ubicacion_id: Optional[int] = None,
    ) -> List[Stock]:
        stmt = select(StockModel)
        if ubicacion_tipo:
            stmt = stmt.where(StockModel.ubicacion_tipo == ubicacion_tipo.value)
        if ubicacion_id is not None:
            stmt = stmt.where(StockModel.ubicacion_id == ubicacion_id)
        return [_stock_to_domain(m) for m in self.db.execute(stmt).scalars()]

    def crear(self, stock: Stock) -> Stock:
        m = StockModel(
            producto_id=stock.producto_id,
            ubicacion_tipo=stock.ubicacion_tipo.value,
            ubicacion_id=stock.ubicacion_id,
            cantidad=stock.cantidad,
            stock_minimo=stock.stock_minimo,
            stock_maximo=stock.stock_maximo,
        )
        self.db.add(m)
        self.db.flush()
        return _stock_to_domain(m)

    def actualizar(self, stock: Stock) -> Stock:
        m = self.db.get(StockModel, stock.id)
        if not m:
            raise ValueError("Stock no existe")
        m.cantidad = stock.cantidad
        m.stock_minimo = stock.stock_minimo
        m.stock_maximo = stock.stock_maximo
        self.db.flush()
        return _stock_to_domain(m)


# ---------- Repositorio Venta ----------

class SqlAlchemyVentaRepository(RepositorioVenta):
    def __init__(self, db: Session) -> None:
        self.db = db

    def crear(self, venta: Venta) -> Venta:
        m = VentaModel(
            serie=venta.serie,
            numero=venta.numero,
            tipo_comprobante=venta.tipo_comprobante.value,
            sucursal_id=venta.sucursal_id,
            cliente_id=venta.cliente_id,
            usuario_id=venta.usuario_id,
            fecha=venta.fecha,
            subtotal=venta.subtotal,
            igv=venta.igv,
            descuento_total=venta.descuento_total,
            total=venta.total,
            estado=venta.estado.value,
            pdf_url=venta.pdf_url,
        )
        self.db.add(m)
        self.db.flush()
        for d in venta.detalles:
            det = DetalleVentaModel(
                venta_id=m.id,
                producto_id=d.producto_id,
                cantidad=d.cantidad,
                precio_unitario=d.precio_unitario,
                descuento=d.descuento,
                igv=d.igv,
                subtotal=d.subtotal,
                total=d.total,
            )
            self.db.add(det)
        self.db.flush()
        return self.obtener_por_id(m.id)

    def obtener_por_id(self, venta_id: int) -> Optional[Venta]:
        stmt = (
            select(VentaModel)
            .options(selectinload(VentaModel.detalles))
            .where(VentaModel.id == venta_id)
        )
        m = self.db.execute(stmt).scalar_one_or_none()
        return _venta_to_domain(m, m.detalles) if m else None

    def listar(
        self,
        sucursal_id: Optional[int] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Venta]:
        stmt = (
            select(VentaModel)
            .options(selectinload(VentaModel.detalles))
            .order_by(VentaModel.fecha.desc())
            .limit(limit)
        )
        if sucursal_id is not None:
            stmt = stmt.where(VentaModel.sucursal_id == sucursal_id)
        if fecha_desde is not None:
            stmt = stmt.where(VentaModel.fecha >= fecha_desde)
        if fecha_hasta is not None:
            stmt = stmt.where(VentaModel.fecha <= fecha_hasta)
        ms = self.db.execute(stmt).scalars().all()
        return [_venta_to_domain(m, m.detalles) for m in ms]

    def anular(self, venta_id: int) -> Venta:
        v = self.obtener_por_id(venta_id)
        if v is None:
            raise ValueError("Venta no existe")
        v.anular()
        m = self.db.get(VentaModel, venta_id)
        m.estado = v.estado.value
        self.db.flush()
        return v

    def siguiente_numero(self, serie: str) -> str:
        stmt = (
            select(VentaModel.numero)
            .where(VentaModel.serie == serie)
            .order_by(VentaModel.id.desc())
            .limit(1)
        )
        ultimo = self.db.execute(stmt).scalar_one_or_none()
        if not ultimo:
            return "00000001"
        try:
            n = int(ultimo) + 1
            return str(n).zfill(8)
        except ValueError:
            return "00000001"


# ---------- Repositorio Solicitud ----------

class SqlAlchemySolicitudRepository(RepositorioSolicitud):
    def __init__(self, db: Session) -> None:
        self.db = db

    def crear(self, solicitud: SolicitudReposicion) -> SolicitudReposicion:
        m = SolicitudModel(
            codigo=solicitud.codigo,
            sucursal_origen_id=solicitud.sucursal_origen_id,
            almacen_destino_id=solicitud.almacen_destino_id,
            usuario_solicita_id=solicitud.usuario_solicita_id,
            estado=solicitud.estado.value,
            motivo=solicitud.motivo,
            fecha_solicitud=solicitud.fecha_solicitud,
        )
        self.db.add(m)
        self.db.flush()
        for d in solicitud.detalles:
            det = DetalleSolicitudModel(
                solicitud_id=m.id,
                producto_id=d.producto_id,
                cantidad_solicitada=d.cantidad_solicitada,
            )
            self.db.add(det)
        self.db.flush()
        return self.obtener_por_id(m.id)

    def obtener_por_id(self, solicitud_id: int) -> Optional[SolicitudReposicion]:
        m = self.db.get(SolicitudModel, solicitud_id)
        if not m:
            return None
        stmt = select(DetalleSolicitudModel).where(
            DetalleSolicitudModel.solicitud_id == solicitud_id
        )
        detalles = self.db.execute(stmt).scalars().all()
        return _solicitud_to_domain(m, detalles)

    def listar(
        self,
        sucursal_id: Optional[int] = None,
        estado: Optional[EstadoSolicitud] = None,
    ) -> List[SolicitudReposicion]:
        stmt = select(SolicitudModel).order_by(SolicitudModel.id.desc())
        if sucursal_id is not None:
            stmt = stmt.where(SolicitudModel.sucursal_origen_id == sucursal_id)
        if estado is not None:
            stmt = stmt.where(SolicitudModel.estado == estado.value)
        ms = self.db.execute(stmt).scalars().all()
        resultado: List[SolicitudReposicion] = []
        for m in ms:
            dets = self.db.execute(
                select(DetalleSolicitudModel).where(
                    DetalleSolicitudModel.solicitud_id == m.id
                )
            ).scalars().all()
            resultado.append(_solicitud_to_domain(m, dets))
        return resultado

    def actualizar(self, solicitud: SolicitudReposicion) -> SolicitudReposicion:
        m = self.db.get(SolicitudModel, solicitud.id)
        if not m:
            raise ValueError("Solicitud no existe")
        m.estado = solicitud.estado.value
        m.usuario_evalua_id = solicitud.usuario_evalua_id
        m.observacion = solicitud.observacion
        m.fecha_evaluacion = solicitud.fecha_evaluacion
        m.fecha_envio = solicitud.fecha_envio
        m.fecha_recepcion = solicitud.fecha_recepcion
        self.db.flush()
        return self.obtener_por_id(m.id)


# ---------- Repositorio Alerta ----------

class SqlAlchemyAlertaRepository(RepositorioAlerta):
    def __init__(self, db: Session) -> None:
        self.db = db

    def crear(self, alerta: Alerta) -> Alerta:
        m = AlertaModel(
            tipo=alerta.tipo.value,
            producto_id=alerta.producto_id,
            ubicacion_tipo=alerta.ubicacion_tipo,
            ubicacion_id=alerta.ubicacion_id,
            cantidad_actual=alerta.cantidad_actual,
            stock_referencia=alerta.stock_referencia,
            estado=alerta.estado.value,
            mensaje=alerta.mensaje,
        )
        self.db.add(m)
        self.db.flush()
        return _alerta_to_domain(m)

    def listar(
        self,
        tipo: Optional[TipoAlerta] = None,
        estado: Optional[EstadoAlerta] = None,
        ubicacion_id: Optional[int] = None,
    ) -> List[Alerta]:
        stmt = select(AlertaModel).order_by(AlertaModel.id.desc())
        if tipo is not None:
            stmt = stmt.where(AlertaModel.tipo == tipo.value)
        if estado is not None:
            stmt = stmt.where(AlertaModel.estado == estado.value)
        if ubicacion_id is not None:
            stmt = stmt.where(AlertaModel.ubicacion_id == ubicacion_id)
        return [_alerta_to_domain(m) for m in self.db.execute(stmt).scalars()]

    def atender(self, alerta_id: int) -> Alerta:
        m = self.db.get(AlertaModel, alerta_id)
        if not m:
            raise ValueError("Alerta no existe")
        m.estado = EstadoAlerta.ATENDIDA.value
        m.atendida_at = datetime.utcnow()
        self.db.flush()
        return _alerta_to_domain(m)

    def descartar(self, alerta_id: int) -> Alerta:
        m = self.db.get(AlertaModel, alerta_id)
        if not m:
            raise ValueError("Alerta no existe")
        m.estado = EstadoAlerta.DESCARTADA.value
        m.atendida_at = datetime.utcnow()
        self.db.flush()
        return _alerta_to_domain(m)
