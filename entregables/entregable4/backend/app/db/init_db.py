from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.constants import ROLES_BASE
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.categoria import Categoria
from app.models.cliente import Cliente
from app.models.metodo_pago import MetodoPago
from app.models.venta import Venta, DetalleVenta
from app.models.orden_compra import OrdenCompra, DetalleOrdenCompra
from app.models.solicitud_reposicion import SolicitudReposicion, DetalleSolicitudReposicion
from app.models.empresa import Empresa
from app.models.producto import Producto
from app.models.alerta_stock import AlertaStock
from app.models.movimiento_inventario import MovimientoInventario
from app.models.inventario_ubicacion import InventarioUbicacion
from app.models.proveedor import Proveedor
from app.models.rol import Rol
from app.models.ubicacion import Ubicacion
from app.models.usuario import Usuario
from app.models.codigo_verificacion import CodigoVerificacion
from app.models.sesion_usuario import SesionUsuario
from app.utils.password import generar_hash_contrasena


UBICACIONES_BASE = [
    {
        "nombreUbicacion": "Almacen Central",
        "tipoUbicacion": "ALMACEN",
        "direccion": "Av. Principal 123 - Lima",
    },
    {
        "nombreUbicacion": "Sucursal Norte",
        "tipoUbicacion": "SUCURSAL",
        "direccion": "Av. Tupac Amaru 450 - Los Olivos",
    },
    {
        "nombreUbicacion": "Sucursal Sur",
        "tipoUbicacion": "SUCURSAL",
        "direccion": "Av. Caminos del Inca 456 - Surco",
    },
    {
        "nombreUbicacion": "Sucursal Centro",
        "tipoUbicacion": "SUCURSAL",
        "direccion": "Jr. de la Union 320 - Cercado de Lima",
    },
    {
        "nombreUbicacion": "Sucursal Este",
        "tipoUbicacion": "SUCURSAL",
        "direccion": "Av. Proceres 820 - San Juan de Lurigancho",
    },
]

USUARIOS_INICIALES = [
    {
        "correoElectronico": "codexventa@gmail.com",
        "contrasena": "Admin123*",
        "rol": "ADMIN",
        "ubicacion": "Almacen Central",
    },
    {
        "correoElectronico": "crhistiandionicio17@gmail.com",
        "contrasena": "Almacen123*",
        "rol": "SUPERVISOR_ALMACEN",
        "ubicacion": "Almacen Central",
    },
    {
        "correoElectronico": "richardesteban53@gmail.com",
        "contrasena": "Sucursal123*",
        "rol": "SUPERVISOR_SUCURSAL",
        "ubicacion": "Sucursal Norte",
    },
    {
        "correoElectronico": "gonzaloventuro@gmail.com",
        "contrasena": "Sucursal123*",
        "rol": "SUPERVISOR_SUCURSAL",
        "ubicacion": "Sucursal Sur",
    },
    {
        "correoElectronico": "marquinachahuayoj@gmail.com",
        "contrasena": "Vendedor123*",
        "rol": "VENDEDOR",
        "ubicacion": "Sucursal Norte",
    },
]

CUENTAS_DEMO_ANTERIORES = [
    "admin@demo.com",
    "almacen@demo.com",
    "sucursal@demo.com",
    "sucursal.sur@demo.com",
    "sucursal.centro@demo.com",
    "sucursal.este@demo.com",
    "vendedor@demo.com",
]


PROVEEDORES_INICIALES = [
    {
        "identificacionFiscal": "20123456789",
        "razonSocial": "Distribuidora Andina SAC",
        "contactoNombre": "Maria Torres",
        "telefono": "987654321",
        "correoElectronico": "ventas@distribuidoraandina.com",
        "direccion": "Av. Argentina 1500 - Lima",
    },
    {
        "identificacionFiscal": "20456789123",
        "razonSocial": "Mayorista Peru SAC",
        "contactoNombre": "Carlos Rivas",
        "telefono": "976543210",
        "correoElectronico": "pedidos@mayoristaperu.com",
        "direccion": "Av. Industrial 980 - Ate",
    },
    {
        "identificacionFiscal": "20678912345",
        "razonSocial": "Comercial Lima EIRL",
        "contactoNombre": "Ana Salazar",
        "telefono": "965432109",
        "correoElectronico": "contacto@comerciallima.com",
        "direccion": "Jr. Huancavelica 620 - Cercado de Lima",
    },
]

CATEGORIAS_INICIALES = [
    {"nombreCategoria": "Abarrotes", "descripcion": "Productos basicos de consumo diario"},
    {"nombreCategoria": "Lacteos", "descripcion": "Leche y productos derivados"},
    {"nombreCategoria": "Limpieza", "descripcion": "Productos de limpieza del hogar"},
]

PRODUCTOS_INICIALES = [
    {"codigoBarras": "7750001000011", "nombreProducto": "Arroz Costeno 5 kg", "precioVenta": Decimal("23.90"), "porcentajeIgv": Decimal("18.00"), "categoria": "Abarrotes"},
    {"codigoBarras": "7750001000028", "nombreProducto": "Aceite Primor 1 L", "precioVenta": Decimal("11.50"), "porcentajeIgv": Decimal("18.00"), "categoria": "Abarrotes"},
    {"codigoBarras": "7750001000035", "nombreProducto": "Azucar rubia 1 kg", "precioVenta": Decimal("4.20"), "porcentajeIgv": Decimal("18.00"), "categoria": "Abarrotes"},
    {"codigoBarras": "7750001000042", "nombreProducto": "Leche evaporada Gloria 400 g", "precioVenta": Decimal("4.80"), "porcentajeIgv": Decimal("18.00"), "categoria": "Lacteos"},
    {"codigoBarras": "7750001000059", "nombreProducto": "Detergente Bolivar 800 g", "precioVenta": Decimal("12.90"), "porcentajeIgv": Decimal("18.00"), "categoria": "Limpieza"},
    {"codigoBarras": "7750001000066", "nombreProducto": "Fideos Don Vittorio 500 g", "precioVenta": Decimal("4.50"), "porcentajeIgv": Decimal("18.00"), "categoria": "Abarrotes"},
]

STOCK_SUCURSALES_INICIAL = {
    "Sucursal Norte": {
        "7750001000011": (8, 10),
        "7750001000028": (5, 8),
        "7750001000042": (12, 10),
    },
    "Sucursal Sur": {
        "7750001000011": (6, 10),
        "7750001000035": (4, 8),
        "7750001000066": (15, 10),
    },
    "Sucursal Centro": {
        "7750001000028": (3, 8),
        "7750001000042": (7, 10),
        "7750001000059": (6, 5),
    },
    "Sucursal Este": {
        "7750001000011": (0, 10),
        "7750001000035": (2, 8),
        "7750001000066": (9, 10),
    },
}


def _money(valor: Decimal) -> Decimal:
    return valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _crear_o_obtener_proveedor(db: Session, empresa: Empresa, datos: dict) -> Proveedor:
    proveedor = db.query(Proveedor).filter(
        Proveedor.identificacionFiscal == datos["identificacionFiscal"]
    ).first()

    if proveedor:
        return proveedor

    proveedor = Proveedor(
        idEmpresa=empresa.idEmpresa,
        identificacionFiscal=datos["identificacionFiscal"],
        razonSocial=datos["razonSocial"],
        contactoNombre=datos["contactoNombre"],
        telefono=datos["telefono"],
        correoElectronico=datos["correoElectronico"],
        direccion=datos["direccion"],
        isActivo=True,
    )
    db.add(proveedor)
    db.flush()
    return proveedor


def _crear_o_obtener_producto(db: Session, empresa: Empresa, datos: dict) -> Producto:
    producto = db.query(Producto).filter(
        Producto.codigoBarras == datos["codigoBarras"]
    ).first()

    categoria = None
    if datos.get("categoria"):
        categoria = db.query(Categoria).filter(
            Categoria.idEmpresa == empresa.idEmpresa,
            Categoria.nombreCategoria == datos["categoria"]
        ).first()

    if producto:
        if categoria and producto.idCategoria != categoria.idCategoria:
            producto.idCategoria = categoria.idCategoria
            db.flush()
        return producto

    producto = Producto(
        idEmpresa=empresa.idEmpresa,
        idCategoria=categoria.idCategoria if categoria else None,
        codigoBarras=datos["codigoBarras"],
        nombreProducto=datos["nombreProducto"],
        precioVenta=datos["precioVenta"],
        porcentajeIgv=datos["porcentajeIgv"],
        isActivo=True,
    )
    db.add(producto)
    db.flush()
    return producto


def _asegurar_inventario(
    db: Session,
    ubicacion: Ubicacion,
    producto: Producto,
    stock_disponible: int = 0,
    stock_minimo: int = 0,
) -> InventarioUbicacion:
    inventario = db.query(InventarioUbicacion).filter(
        InventarioUbicacion.idUbicacion == ubicacion.idUbicacion,
        InventarioUbicacion.idProducto == producto.idProducto,
    ).first()

    if inventario:
        if inventario.stockMinimo == 0 and stock_minimo > 0:
            inventario.stockMinimo = stock_minimo
        return inventario

    inventario = InventarioUbicacion(
        idUbicacion=ubicacion.idUbicacion,
        idProducto=producto.idProducto,
        stockDisponible=stock_disponible,
        stockMinimo=stock_minimo,
    )
    db.add(inventario)
    db.flush()
    return inventario


def _calcular_totales_orden(detalles: list[tuple[Producto, int, Decimal]]):
    total_neto = Decimal("0.00")
    total_igv = Decimal("0.00")
    total_compra = Decimal("0.00")

    for producto, cantidad, precio_unitario in detalles:
        total_linea = _money(Decimal(cantidad) * precio_unitario)
        porcentaje_igv = Decimal(str(producto.porcentajeIgv or 0))

        if porcentaje_igv > 0:
            divisor = Decimal("1.00") + porcentaje_igv / Decimal("100.00")
            subtotal_linea = _money(total_linea / divisor)
            igv_linea = _money(total_linea - subtotal_linea)
        else:
            subtotal_linea = total_linea
            igv_linea = Decimal("0.00")

        total_neto += subtotal_linea
        total_igv += igv_linea
        total_compra += total_linea

    return _money(total_neto), _money(total_igv), _money(total_compra)


def _crear_orden_inicial(
    db: Session,
    proveedor: Proveedor,
    almacen_central: Ubicacion,
    usuario_comprador: Usuario,
    detalles: list[tuple[Producto, int, Decimal]],
    estado: str,
    usuario_receptor: Usuario | None = None,
    dias_atras: int = 0,
) -> OrdenCompra:
    total_neto, total_igv, total_compra = _calcular_totales_orden(detalles)
    fecha_pedido = datetime.now() - timedelta(days=dias_atras)

    orden = OrdenCompra(
        idProveedor=proveedor.idProveedor,
        idUbicacionDestino=almacen_central.idUbicacion,
        idUsuarioComprador=usuario_comprador.idUsuario,
        idUsuarioReceptor=(usuario_receptor.idUsuario if estado == "RECIBIDO" and usuario_receptor else None),
        fechaPedido=fecha_pedido,
        fechaRecepcion=(fecha_pedido + timedelta(hours=6) if estado == "RECIBIDO" else None),
        estado=estado,
        totalNeto=total_neto,
        totalIgv=total_igv,
        totalCompra=total_compra,
    )
    db.add(orden)
    db.flush()

    for producto, cantidad, precio_unitario in detalles:
        db.add(DetalleOrdenCompra(
            idOrdenCompra=orden.idOrdenCompra,
            idProducto=producto.idProducto,
            cantidadPedida=cantidad,
            cantidadRecibida=(cantidad if estado == "RECIBIDO" else 0),
            precioCompraUnitario=precio_unitario,
        ))

        if estado == "RECIBIDO" and usuario_receptor:
            inventario = _asegurar_inventario(db, almacen_central, producto, stock_disponible=0, stock_minimo=10)
            inventario.stockDisponible += cantidad
            db.add(MovimientoInventario(
                idUbicacion=almacen_central.idUbicacion,
                idProducto=producto.idProducto,
                idUsuario=usuario_receptor.idUsuario,
                cantidad=cantidad,
                tipoMovimiento="INGRESO",
                motivoMovimiento="COMPRA_PROVEEDOR",
                tipoReferencia="ORDEN_COMPRA",
                idReferencia=orden.idOrdenCompra,
            ))

    db.flush()
    return orden



def _crear_alerta_inicial_si_corresponde(db: Session, inventario: InventarioUbicacion):
    tipo_alerta = None
    if inventario.stockDisponible == 0:
        tipo_alerta = "STOCK_AGOTADO"
    elif inventario.stockDisponible <= inventario.stockMinimo:
        tipo_alerta = "STOCK_MINIMO"

    if not tipo_alerta:
        return

    alerta_existente = db.query(AlertaStock).filter(
        AlertaStock.idUbicacion == inventario.idUbicacion,
        AlertaStock.idProducto == inventario.idProducto,
        AlertaStock.tipoAlerta == tipo_alerta,
        AlertaStock.estado == "PENDIENTE",
    ).first()

    if alerta_existente:
        alerta_existente.cantidadActual = inventario.stockDisponible
        alerta_existente.stockReferencia = inventario.stockMinimo
        return

    db.add(AlertaStock(
        idUbicacion=inventario.idUbicacion,
        idProducto=inventario.idProducto,
        tipoAlerta=tipo_alerta,
        cantidadActual=inventario.stockDisponible,
        stockReferencia=inventario.stockMinimo,
        estado="PENDIENTE",
    ))


def _crear_reposicion_inicial(
    db: Session,
    almacen_central: Ubicacion,
    sucursal: Ubicacion,
    usuario_solicitante: Usuario,
    usuario_despachador: Usuario | None,
    usuario_receptor: Usuario | None,
    detalles: list[tuple[Producto, int]],
    estado: str,
    observacion: str,
    dias_atras: int = 0,
) -> SolicitudReposicion:
    fecha_solicitud = datetime.now() - timedelta(days=dias_atras)
    solicitud = SolicitudReposicion(
        idUbicacionOrigen=almacen_central.idUbicacion,
        idUbicacionDestino=sucursal.idUbicacion,
        idUsuarioSolicitante=usuario_solicitante.idUsuario,
        idUsuarioDespachador=(usuario_despachador.idUsuario if estado in ("EN_TRANSITO", "RECIBIDA") and usuario_despachador else None),
        idUsuarioReceptor=(usuario_receptor.idUsuario if estado == "RECIBIDA" and usuario_receptor else None),
        fechaSolicitud=fecha_solicitud,
        fechaAperturaRevision=(fecha_solicitud + timedelta(hours=2) if estado in ("EN_REVISION", "ACEPTADO", "EN_TRANSITO", "RECIBIDA", "RECHAZADA") else None),
        fechaDespacho=(fecha_solicitud + timedelta(hours=5) if estado in ("EN_TRANSITO", "RECIBIDA") else None),
        fechaRecepcion=(fecha_solicitud + timedelta(hours=9) if estado == "RECIBIDA" else None),
        estado=estado,
        observacion=observacion,
    )
    db.add(solicitud)
    db.flush()

    for producto, cantidad in detalles:
        cantidad_despachada = cantidad if estado in ("EN_TRANSITO", "RECIBIDA") else 0
        db.add(DetalleSolicitudReposicion(
            idSolicitud=solicitud.idSolicitud,
            idProducto=producto.idProducto,
            cantidadSolicitada=cantidad,
            cantidadDespachada=cantidad_despachada,
        ))

        if estado in ("EN_TRANSITO", "RECIBIDA") and usuario_despachador:
            inv_origen = _asegurar_inventario(db, almacen_central, producto, stock_disponible=0, stock_minimo=10)
            if inv_origen.stockDisponible >= cantidad:
                inv_origen.stockDisponible -= cantidad
            db.add(MovimientoInventario(
                idUbicacion=almacen_central.idUbicacion,
                idProducto=producto.idProducto,
                idUsuario=usuario_despachador.idUsuario,
                cantidad=cantidad,
                tipoMovimiento="SALIDA",
                motivoMovimiento="REPOSICION_ENVIADA",
                tipoReferencia="SOLICITUD_REPOSICION",
                idReferencia=solicitud.idSolicitud,
            ))
            _crear_alerta_inicial_si_corresponde(db, inv_origen)

        if estado == "RECIBIDA" and usuario_receptor:
            inv_destino = _asegurar_inventario(db, sucursal, producto, stock_disponible=0, stock_minimo=10)
            inv_destino.stockDisponible += cantidad
            db.add(MovimientoInventario(
                idUbicacion=sucursal.idUbicacion,
                idProducto=producto.idProducto,
                idUsuario=usuario_receptor.idUsuario,
                cantidad=cantidad,
                tipoMovimiento="INGRESO",
                motivoMovimiento="REPOSICION_RECIBIDA",
                tipoReferencia="SOLICITUD_REPOSICION",
                idReferencia=solicitud.idSolicitud,
            ))
            _crear_alerta_inicial_si_corresponde(db, inv_destino)

    db.flush()
    return solicitud

def seed_datos_operativos_iniciales(db: Session, empresa: Empresa):
    """Carga datos operativos iniciales para simular ordenes de compra, recepciones e inventario."""
    proveedores = {
        datos["razonSocial"]: _crear_o_obtener_proveedor(db, empresa, datos)
        for datos in PROVEEDORES_INICIALES
    }
    productos = {
        datos["codigoBarras"]: _crear_o_obtener_producto(db, empresa, datos)
        for datos in PRODUCTOS_INICIALES
    }

    ubicaciones = {
        ubicacion.nombreUbicacion: ubicacion
        for ubicacion in db.query(Ubicacion).filter(Ubicacion.idEmpresa == empresa.idEmpresa).all()
    }
    almacen_central = ubicaciones.get("Almacen Central")
    if not almacen_central:
        return

    for producto in productos.values():
        _asegurar_inventario(db, almacen_central, producto, stock_disponible=0, stock_minimo=10)

    for nombre_sucursal, stocks in STOCK_SUCURSALES_INICIAL.items():
        sucursal = ubicaciones.get(nombre_sucursal)
        if not sucursal:
            continue
        for codigo_barras, (stock, stock_minimo) in stocks.items():
            producto = productos.get(codigo_barras)
            if producto:
                inventario = _asegurar_inventario(db, sucursal, producto, stock_disponible=stock, stock_minimo=stock_minimo)
                _crear_alerta_inicial_si_corresponde(db, inventario)

    if db.query(OrdenCompra).first():
        return

    usuario_admin = db.query(Usuario).filter(Usuario.correoElectronico == "codexventa@gmail.com").first()
    usuario_almacen = db.query(Usuario).filter(Usuario.correoElectronico == "crhistiandionicio17@gmail.com").first()
    if not usuario_admin:
        return

    _crear_orden_inicial(
        db=db,
        proveedor=proveedores["Mayorista Peru SAC"],
        almacen_central=almacen_central,
        usuario_comprador=usuario_admin,
        usuario_receptor=usuario_almacen,
        estado="RECIBIDO",
        dias_atras=3,
        detalles=[
            (productos["7750001000035"], 50, Decimal("3.20")),
            (productos["7750001000042"], 60, Decimal("4.10")),
            (productos["7750001000066"], 40, Decimal("3.40")),
        ],
    )

    _crear_orden_inicial(
        db=db,
        proveedor=proveedores["Distribuidora Andina SAC"],
        almacen_central=almacen_central,
        usuario_comprador=usuario_admin,
        usuario_receptor=None,
        estado="SOLICITADO",
        dias_atras=1,
        detalles=[
            (productos["7750001000011"], 20, Decimal("18.50")),
            (productos["7750001000028"], 30, Decimal("9.50")),
            (productos["7750001000059"], 25, Decimal("8.90")),
        ],
    )

    if not db.query(SolicitudReposicion).first() and usuario_almacen:
        supervisor_norte = db.query(Usuario).filter(Usuario.correoElectronico == "richardesteban53@gmail.com").first()
        supervisor_sur = db.query(Usuario).filter(Usuario.correoElectronico == "gonzaloventuro@gmail.com").first()
        sucursal_norte = ubicaciones.get("Sucursal Norte")
        sucursal_sur = ubicaciones.get("Sucursal Sur")

        if supervisor_norte and sucursal_norte:
            _crear_reposicion_inicial(
                db=db,
                almacen_central=almacen_central,
                sucursal=sucursal_norte,
                usuario_solicitante=supervisor_norte,
                usuario_despachador=None,
                usuario_receptor=None,
                estado="ENVIADO",
                observacion="Reposicion solicitada por stock bajo en productos de alta rotacion.",
                dias_atras=0,
                detalles=[
                    (productos["7750001000011"], 12),
                    (productos["7750001000028"], 8),
                ],
            )
            _crear_reposicion_inicial(
                db=db,
                almacen_central=almacen_central,
                sucursal=sucursal_norte,
                usuario_solicitante=supervisor_norte,
                usuario_despachador=usuario_almacen,
                usuario_receptor=None,
                estado="EN_TRANSITO",
                observacion="Mercaderia despachada desde almacen central. Pendiente de confirmacion por sucursal.",
                dias_atras=1,
                detalles=[
                    (productos["7750001000042"], 10),
                    (productos["7750001000066"], 6),
                ],
            )
            _crear_reposicion_inicial(
                db=db,
                almacen_central=almacen_central,
                sucursal=sucursal_norte,
                usuario_solicitante=supervisor_norte,
                usuario_despachador=usuario_almacen,
                usuario_receptor=supervisor_norte,
                estado="RECIBIDA",
                observacion="Recepcion completa sin incidencias.",
                dias_atras=4,
                detalles=[
                    (productos["7750001000035"], 10),
                ],
            )

        if supervisor_sur and sucursal_sur:
            _crear_reposicion_inicial(
                db=db,
                almacen_central=almacen_central,
                sucursal=sucursal_sur,
                usuario_solicitante=supervisor_sur,
                usuario_despachador=None,
                usuario_receptor=None,
                estado="EN_REVISION",
                observacion="Solicitud tomada en revision por almacen central.",
                dias_atras=2,
                detalles=[
                    (productos["7750001000035"], 6),
                    (productos["7750001000066"], 4),
                ],
            )

def ensure_compatibility_columns():
    """Aplica ajustes minimos para bases Docker ya creadas con versiones anteriores."""
    with engine.begin() as connection:
        has_cliente_is_activo = connection.execute(text("""
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'cliente'
              AND COLUMN_NAME = 'isActivo'
        """)).scalar()

        if not has_cliente_is_activo:
            connection.execute(text("ALTER TABLE cliente ADD COLUMN isActivo BOOLEAN NOT NULL DEFAULT TRUE"))

        has_producto_categoria = connection.execute(text("""
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'producto'
              AND COLUMN_NAME = 'idCategoria'
        """)).scalar()

        if not has_producto_categoria:
            connection.execute(text("ALTER TABLE producto ADD COLUMN idCategoria INT NULL AFTER idEmpresa"))

        has_producto_categoria_fk = connection.execute(text("""
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'producto'
              AND COLUMN_NAME = 'idCategoria'
              AND REFERENCED_TABLE_NAME = 'categoria'
              AND REFERENCED_COLUMN_NAME = 'idCategoria'
        """)).scalar()

        if not has_producto_categoria_fk:
            connection.execute(text("""
                ALTER TABLE producto
                ADD CONSTRAINT fk_producto_categoria
                FOREIGN KEY (idCategoria) REFERENCES categoria(idCategoria)
            """))

        has_codigo_hash = connection.execute(text("""
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'codigoverificacion'
              AND COLUMN_NAME = 'codigoHash'
        """)).scalar()

        if not has_codigo_hash:
            connection.execute(text("ALTER TABLE codigoverificacion ADD COLUMN codigoHash VARCHAR(255) NULL AFTER idUsuario"))

        has_codigo_plain = connection.execute(text("""
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'codigoverificacion'
              AND COLUMN_NAME = 'codigo'
        """)).scalar()

        if has_codigo_plain:
            connection.execute(text("ALTER TABLE codigoverificacion MODIFY codigo VARCHAR(6) NULL"))

        has_intentos = connection.execute(text("""
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'codigoverificacion'
              AND COLUMN_NAME = 'intentos'
        """)).scalar()

        if not has_intentos:
            connection.execute(text("ALTER TABLE codigoverificacion ADD COLUMN intentos INT NOT NULL DEFAULT 0 AFTER isUsado"))

        has_fecha_creacion = connection.execute(text("""
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'codigoverificacion'
              AND COLUMN_NAME = 'fechaCreacion'
        """)).scalar()

        if not has_fecha_creacion:
            connection.execute(text("ALTER TABLE codigoverificacion ADD COLUMN fechaCreacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP AFTER intentos"))

        has_fecha_uso = connection.execute(text("""
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'codigoverificacion'
              AND COLUMN_NAME = 'fechaUso'
        """)).scalar()

        if not has_fecha_uso:
            connection.execute(text("ALTER TABLE codigoverificacion ADD COLUMN fechaUso DATETIME NULL AFTER fechaExpiracion"))


def init_db():
    print("INIT_DB SE ESTA EJECUTANDO")

    # Crea las tablas de la Fase 1 a la Fase 6 si todavia no existen.
    # En Docker tambien se usa database/01_schema.sql, pero esto ayuda en desarrollo local.
    Base.metadata.create_all(bind=engine)
    ensure_compatibility_columns()

    db: Session = SessionLocal()

    try:
        # Si database/02_seed_base.sql ya cargo el seed completo de presentacion,
        # no se vuelven a crear datos base. Esto evita duplicar Almacen Central
        # o agregar datos antiguos al iniciar el backend.
        seed_presentacion_cargado = (
            db.query(Venta).first() is not None
            or db.query(Producto).count() >= 30
        )
        if seed_presentacion_cargado:
            db.query(SesionUsuario).filter(SesionUsuario.isActiva.is_(True)).update({
                SesionUsuario.isActiva: False,
                SesionUsuario.fechaCierre: datetime(2026, 7, 2, 23, 59, 0),
                SesionUsuario.motivoCierre: "INIT_DB_SEED_PRESENTACION",
            })
            db.commit()
            print("Seed de presentacion detectado. Se omite seed automatico del backend.")
            return

        empresa = db.query(Empresa).first()

        if not empresa:
            empresa = Empresa(
                nombreEmpresa="Codex Venta",
                isInicializado=True,
                timer_revision_minutos=60,
                igv_porcentaje=18.00,
                moneda="PEN"
            )
            db.add(empresa)
            db.flush()

        for nombre_rol in ROLES_BASE:
            rol_existente = db.query(Rol).filter(
                Rol.nombreRol == nombre_rol
            ).first()

            if not rol_existente:
                db.add(Rol(nombreRol=nombre_rol))

        db.flush()

        for datos_ubicacion in UBICACIONES_BASE:
            ubicacion_existente = db.query(Ubicacion).filter(
                Ubicacion.nombreUbicacion == datos_ubicacion["nombreUbicacion"]
            ).first()

            if not ubicacion_existente:
                db.add(Ubicacion(
                    idEmpresa=empresa.idEmpresa,
                    nombreUbicacion=datos_ubicacion["nombreUbicacion"],
                    tipoUbicacion=datos_ubicacion["tipoUbicacion"],
                    direccion=datos_ubicacion["direccion"],
                    isActivo=True,
                ))

        db.flush()

        categoria_general = db.query(Categoria).filter(
            Categoria.idEmpresa == empresa.idEmpresa,
            Categoria.nombreCategoria == "General"
        ).first()

        if not categoria_general:
            db.add(Categoria(
                idEmpresa=empresa.idEmpresa,
                nombreCategoria="General",
                descripcion="Categoria base para productos sin clasificacion especifica",
                isActivo=True,
            ))

        for datos_categoria in CATEGORIAS_INICIALES:
            categoria_existente = db.query(Categoria).filter(
                Categoria.idEmpresa == empresa.idEmpresa,
                Categoria.nombreCategoria == datos_categoria["nombreCategoria"]
            ).first()
            if not categoria_existente:
                db.add(Categoria(
                    idEmpresa=empresa.idEmpresa,
                    nombreCategoria=datos_categoria["nombreCategoria"],
                    descripcion=datos_categoria["descripcion"],
                    isActivo=True,
                ))

        db.flush()

        for nombre_metodo in ["EFECTIVO", "TARJETA", "YAPE", "PLIN", "TRANSFERENCIA"]:
            metodo_existente = db.query(MetodoPago).filter(
                MetodoPago.nombreMetodo == nombre_metodo
            ).first()

            if not metodo_existente:
                db.add(MetodoPago(
                    nombreMetodo=nombre_metodo,
                    isActivo=True,
                ))

        db.flush()

        for cuenta in USUARIOS_INICIALES:
            ubicacion_cuenta = db.query(Ubicacion).filter(
                Ubicacion.nombreUbicacion == cuenta["ubicacion"]
            ).first()
            rol_cuenta = db.query(Rol).filter(
                Rol.nombreRol == cuenta["rol"]
            ).first()

            if not ubicacion_cuenta or not rol_cuenta:
                continue

            usuario_existente = db.query(Usuario).filter(
                Usuario.correoElectronico == cuenta["correoElectronico"]
            ).first()

            if not usuario_existente:
                db.add(Usuario(
                    idUbicacion=ubicacion_cuenta.idUbicacion,
                    idRol=rol_cuenta.idRol,
                    correoElectronico=cuenta["correoElectronico"],
                    contrasenaHash=generar_hash_contrasena(cuenta["contrasena"]),
                    isActivo=True,
                    isContrasenaTemporal=True
                ))
            else:
                usuario_existente.idUbicacion = ubicacion_cuenta.idUbicacion
                usuario_existente.idRol = rol_cuenta.idRol
                usuario_existente.isActivo = True

        for correo_anterior in CUENTAS_DEMO_ANTERIORES:
            usuario_anterior = db.query(Usuario).filter(
                Usuario.correoElectronico == correo_anterior
            ).first()
            if usuario_anterior:
                usuario_anterior.isActivo = False

        db.flush()
        # Guardamos primero empresa, roles, ubicaciones, categorias, metodos y usuarios.
        # Asi las cuentas de acceso no se pierden si falla algun dato operativo inicial opcional.
        db.commit()

        try:
            seed_datos_operativos_iniciales(db, empresa)
            db.commit()
            print("Datos iniciales y datos operativos creados correctamente.")
        except Exception as datos_error:
            db.rollback()
            print("Datos base creados. No se pudieron cargar algunos datos operativos iniciales:", datos_error)

        print("Cuentas iniciales por rol:")
        for cuenta in USUARIOS_INICIALES:
            print(f"- {cuenta['rol']}: {cuenta['correoElectronico']} / {cuenta['contrasena']}")

    except Exception as error:
        db.rollback()
        print("Error inicializando la base de datos:", error)

    finally:
        db.close()


if __name__ == "__main__":
    init_db()
