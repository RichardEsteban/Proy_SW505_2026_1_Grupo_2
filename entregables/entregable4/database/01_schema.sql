-- ============================================================================
-- SISTEMA DE INVENTARIO Y VENTAS (POS) — ESQUEMA sistemamype
-- Versión: 2.0 — Piloto
-- Cambios vs attachment original:
--   * Empresa: agregada columna timer_revision_minutos (Plan A pregunta 1)
--   * SolicitudReposicion: enum actualizado a 7 estados (Plan A pregunta 1)
--   * Resto del esquema intacto
-- ============================================================================

CREATE DATABASE IF NOT EXISTS sistemamype;
USE sistemamype;

-- Otorgar permisos al usuario inventario
GRANT ALL PRIVILEGES ON sistemamype.* TO 'inventario'@'%';
FLUSH PRIVILEGES;

-- ============================================================================
-- MÓDULO 1: CONFIGURACIÓN DE EMPRESA Y UBICACIONES
-- ============================================================================

CREATE TABLE empresa (
    idEmpresa INT AUTO_INCREMENT PRIMARY KEY,
    nombreEmpresa VARCHAR(150) NOT NULL,
    isInicializado BOOLEAN NOT NULL DEFAULT FALSE,
    fechaInicializacion DATETIME NULL,
    -- NUEVO: timer configurable por admin para auto-transición ENVIADO→EN_REVISION
    timer_revision_minutos INT NOT NULL DEFAULT 60,
    igv_porcentaje DECIMAL(5,2) NOT NULL DEFAULT 18.00,
    moneda CHAR(3) NOT NULL DEFAULT 'PEN'
) ENGINE=InnoDB;

CREATE TABLE ubicacion (
    idUbicacion INT AUTO_INCREMENT PRIMARY KEY,
    idEmpresa INT NOT NULL,
    nombreUbicacion VARCHAR(150) NOT NULL,
    tipoUbicacion ENUM('ALMACEN', 'SUCURSAL') NOT NULL,
    direccion VARCHAR(255) NOT NULL,
    isActivo BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (idEmpresa) REFERENCES empresa(idEmpresa)
) ENGINE=InnoDB;

-- ============================================================================
-- MÓDULO 2: USUARIOS, ROLES Y SEGURIDAD
-- ============================================================================

CREATE TABLE rol (
    idRol INT AUTO_INCREMENT PRIMARY KEY,
    nombreRol VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE usuario (
    idUsuario INT AUTO_INCREMENT PRIMARY KEY,
    idUbicacion INT NOT NULL,
    idRol INT NOT NULL,
    correoElectronico VARCHAR(150) NOT NULL UNIQUE,
    contrasenaHash VARCHAR(255) NOT NULL,
    isActivo BOOLEAN NOT NULL DEFAULT TRUE,
    isContrasenaTemporal BOOLEAN NOT NULL DEFAULT TRUE,
    fechaCreacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (idUbicacion) REFERENCES ubicacion(idUbicacion),
    FOREIGN KEY (idRol) REFERENCES rol(idRol)
) ENGINE=InnoDB;

CREATE TABLE codigoverificacion (
    idCodigo INT AUTO_INCREMENT PRIMARY KEY,
    idUsuario INT NOT NULL,
    codigo VARCHAR(6) NOT NULL,
    isUsado BOOLEAN NOT NULL DEFAULT FALSE,
    fechaExpiracion DATETIME NOT NULL,
    FOREIGN KEY (idUsuario) REFERENCES usuario(idUsuario)
) ENGINE=InnoDB;

-- ============================================================================
-- MÓDULO 3: CATÁLOGO, PROVEEDORES E INVENTARIO
-- ============================================================================

CREATE TABLE proveedor (
    idProveedor INT AUTO_INCREMENT PRIMARY KEY,
    idEmpresa INT NOT NULL,
    identificacionFiscal VARCHAR(11) NOT NULL UNIQUE,
    razonSocial VARCHAR(150) NOT NULL,
    contactoNombre VARCHAR(100) NULL,
    telefono VARCHAR(20) NULL,
    correoElectronico VARCHAR(150) NULL,
    direccion VARCHAR(255) NULL,
    isActivo BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (idEmpresa) REFERENCES empresa(idEmpresa)
) ENGINE=InnoDB;

CREATE TABLE producto (
    idProducto INT AUTO_INCREMENT PRIMARY KEY,
    idEmpresa INT NOT NULL,
    codigoBarras VARCHAR(50) NOT NULL UNIQUE,
    nombreProducto VARCHAR(150) NOT NULL,
    precioVenta DECIMAL(12,2) NOT NULL,
    porcentajeIgv DECIMAL(5,2) NOT NULL DEFAULT 18.00,
    isActivo BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (idEmpresa) REFERENCES empresa(idEmpresa)
) ENGINE=InnoDB;

CREATE TABLE inventarioubicacion (
    idInventario INT AUTO_INCREMENT PRIMARY KEY,
    idUbicacion INT NOT NULL,
    idProducto INT NOT NULL,
    stockDisponible INT NOT NULL DEFAULT 0,
    stockMinimo INT NOT NULL DEFAULT 0,
    CONSTRAINT UNIQUE_ubicacion_producto UNIQUE (idUbicacion, idProducto),
    CONSTRAINT CHK_stock_disponible CHECK (stockDisponible >= 0),
    CONSTRAINT CHK_stock_minimo CHECK (stockMinimo >= 0),
    FOREIGN KEY (idUbicacion) REFERENCES ubicacion(idUbicacion),
    FOREIGN KEY (idProducto) REFERENCES producto(idProducto)
) ENGINE=InnoDB;

-- ============================================================================
-- MÓDULO 4: TRAZABILIDAD (KARDEX)
-- ============================================================================

CREATE TABLE movimientoinventario (
    idMovimiento INT AUTO_INCREMENT PRIMARY KEY,
    idUbicacion INT NOT NULL,
    idProducto INT NOT NULL,
    idUsuario INT NOT NULL,
    cantidad INT NOT NULL,
    tipoMovimiento ENUM('INGRESO', 'SALIDA') NOT NULL,
    motivoMovimiento ENUM(
        'VENTA',
        'COMPRA_PROVEEDOR',
        'REPOSICION_ENVIADA',
        'REPOSICION_RECIBIDA',
        'MERMA',
        'AJUSTE'
    ) NOT NULL,
    tipoReferencia ENUM('VENTA', 'ORDEN_COMPRA', 'SOLICITUD_REPOSICION') NULL,
    idReferencia INT NULL,
    fechaHora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT CHK_cantidad_positiva CHECK (cantidad > 0),
    FOREIGN KEY (idUbicacion) REFERENCES ubicacion(idUbicacion),
    FOREIGN KEY (idProducto) REFERENCES producto(idProducto),
    FOREIGN KEY (idUsuario) REFERENCES usuario(idUsuario)
) ENGINE=InnoDB;

-- ============================================================================
-- MÓDULO 5: ENTIDADES DE CLIENTES (PADRE-HIJO)
-- ============================================================================

CREATE TABLE cliente (
    idCliente INT AUTO_INCREMENT PRIMARY KEY,
    tipoCliente ENUM('PERSONA', 'EMPRESA') NOT NULL,
    telefono VARCHAR(20) NULL,
    correoElectronico VARCHAR(150) NULL
) ENGINE=InnoDB;

CREATE TABLE persona (
    idCliente INT PRIMARY KEY,
    documentoIdentidad VARCHAR(12) NOT NULL UNIQUE,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    FOREIGN KEY (idCliente) REFERENCES cliente(idCliente) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE empresacliente (
    idCliente INT PRIMARY KEY,
    identificacionFiscal VARCHAR(11) NOT NULL UNIQUE,
    razonSocial VARCHAR(150) NOT NULL,
    direccionFiscal VARCHAR(255) NULL,
    FOREIGN KEY (idCliente) REFERENCES cliente(idCliente) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================================
-- MÓDULO 6: VENTAS Y FACTURACIÓN
-- ============================================================================

CREATE TABLE metodopago (
    idMetodoPago INT AUTO_INCREMENT PRIMARY KEY,
    nombreMetodo VARCHAR(50) NOT NULL UNIQUE,
    isActivo BOOLEAN NOT NULL DEFAULT TRUE
) ENGINE=InnoDB;

CREATE TABLE venta (
    idVenta INT AUTO_INCREMENT PRIMARY KEY,
    idUbicacion INT NOT NULL,
    idUsuario INT NOT NULL,
    idCliente INT NULL,
    idMetodoPago INT NOT NULL,
    fechaHora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    subtotalVenta DECIMAL(12,2) NOT NULL,
    totalIgv DECIMAL(12,2) NOT NULL,
    totalVenta DECIMAL(12,2) NOT NULL,
    pdf_url VARCHAR(255) NULL,
    FOREIGN KEY (idUbicacion) REFERENCES ubicacion(idUbicacion),
    FOREIGN KEY (idUsuario) REFERENCES usuario(idUsuario),
    FOREIGN KEY (idCliente) REFERENCES cliente(idCliente),
    FOREIGN KEY (idMetodoPago) REFERENCES metodopago(idMetodoPago)
) ENGINE=InnoDB;

CREATE TABLE detalleventa (
    idDetalleVenta INT AUTO_INCREMENT PRIMARY KEY,
    idVenta INT NOT NULL,
    idProducto INT NOT NULL,
    cantidad INT NOT NULL,
    precioUnitarioFacturado DECIMAL(12,2) NOT NULL,
    igvAplicado DECIMAL(12,2) NOT NULL,
    subtotal DECIMAL(12,2) NOT NULL,
    CONSTRAINT UNIQUE_venta_producto UNIQUE (idVenta, idProducto),
    CONSTRAINT CHK_venta_cantidad CHECK (cantidad > 0),
    FOREIGN KEY (idVenta) REFERENCES venta(idVenta) ON DELETE CASCADE,
    FOREIGN KEY (idProducto) REFERENCES producto(idProducto)
) ENGINE=InnoDB;

-- ============================================================================
-- MÓDULO 7: ABASTECIMIENTO EXTERNO (PROVEEDORES)
-- ============================================================================

CREATE TABLE ordencompra (
    idOrdenCompra INT AUTO_INCREMENT PRIMARY KEY,
    idProveedor INT NOT NULL,
    idUbicacionDestino INT NOT NULL,
    idUsuarioComprador INT NOT NULL,
    idUsuarioReceptor INT NULL,
    fechaPedido DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fechaRecepcion DATETIME NULL,
    estado ENUM('SOLICITADO', 'EN_TRANSITO', 'RECIBIDO', 'CANCELADO') NOT NULL DEFAULT 'SOLICITADO',
    totalNeto DECIMAL(12,2) NOT NULL,
    totalIgv DECIMAL(12,2) NOT NULL,
    totalCompra DECIMAL(12,2) NOT NULL,
    FOREIGN KEY (idProveedor) REFERENCES proveedor(idProveedor),
    FOREIGN KEY (idUbicacionDestino) REFERENCES ubicacion(idUbicacion),
    FOREIGN KEY (idUsuarioComprador) REFERENCES usuario(idUsuario),
    FOREIGN KEY (idUsuarioReceptor) REFERENCES usuario(idUsuario)
) ENGINE=InnoDB;

CREATE TABLE detalleordencompra (
    idDetalleOrden INT AUTO_INCREMENT PRIMARY KEY,
    idOrdenCompra INT NOT NULL,
    idProducto INT NOT NULL,
    cantidadPedida INT NOT NULL,
    cantidadRecibida INT NOT NULL DEFAULT 0,
    precioCompraUnitario DECIMAL(12,2) NOT NULL,
    CONSTRAINT UNIQUE_orden_producto UNIQUE (idOrdenCompra, idProducto),
    CONSTRAINT CHK_compra_cantidad CHECK (cantidadPedida > 0),
    FOREIGN KEY (idOrdenCompra) REFERENCES ordencompra(idOrdenCompra) ON DELETE CASCADE,
    FOREIGN KEY (idProducto) REFERENCES producto(idProducto)
) ENGINE=InnoDB;

-- ============================================================================
-- MÓDULO 8: LOGÍSTICA INTERNA (REPOSICIONES)
-- 7 ESTADOS (Plan A pregunta 1):
--   ENVIADO → EN_REVISION → ACEPTADO → EN_TRANSITO → RECIBIDA | RECHAZADA
--   En cualquier momento antes de ACEPTADO → CANCELADA (vía CU-09)
-- ============================================================================

CREATE TABLE solicitudreposicion (
    idSolicitud INT AUTO_INCREMENT PRIMARY KEY,
    idUbicacionOrigen INT NOT NULL,
    idUbicacionDestino INT NOT NULL,
    idUsuarioSolicitante INT NOT NULL,
    idUsuarioDespachador INT NULL,
    idUsuarioReceptor INT NULL,
    fechaSolicitud DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fechaDespacho DATETIME NULL,
    fechaRecepcion DATETIME NULL,
    -- Plan A: 7 estados
    estado ENUM(
        'ENVIADO',
        'EN_REVISION',
        'ACEPTADO',
        'EN_TRANSITO',
        'RECIBIDA',
        'RECHAZADA',
        'CANCELADA'
    ) NOT NULL DEFAULT 'ENVIADO',
    observacion TEXT NULL,
    fechaAperturaRevision DATETIME NULL,
    FOREIGN KEY (idUbicacionOrigen) REFERENCES ubicacion(idUbicacion),
    FOREIGN KEY (idUbicacionDestino) REFERENCES ubicacion(idUbicacion),
    FOREIGN KEY (idUsuarioSolicitante) REFERENCES usuario(idUsuario),
    FOREIGN KEY (idUsuarioDespachador) REFERENCES usuario(idUsuario),
    FOREIGN KEY (idUsuarioReceptor) REFERENCES usuario(idUsuario)
) ENGINE=InnoDB;

CREATE TABLE detallesolicitudreposicion (
    idDetalleSolicitud INT AUTO_INCREMENT PRIMARY KEY,
    idSolicitud INT NOT NULL,
    idProducto INT NOT NULL,
    cantidadSolicitada INT NOT NULL,
    cantidadDespachada INT NOT NULL DEFAULT 0,
    CONSTRAINT UNIQUE_solicitud_producto UNIQUE (idSolicitud, idProducto),
    CONSTRAINT CHK_reposicion_cantidad CHECK (cantidadSolicitada > 0),
    FOREIGN KEY (idSolicitud) REFERENCES solicitudreposicion(idSolicitud) ON DELETE CASCADE,
    FOREIGN KEY (idProducto) REFERENCES producto(idProducto)
) ENGINE=InnoDB;

-- ============================================================================
-- MÓDULO 9: ALERTAS DE STOCK (NUEVO — para CU-07)
-- ============================================================================

CREATE TABLE alertastock (
    idAlerta INT AUTO_INCREMENT PRIMARY KEY,
    idUbicacion INT NOT NULL,
    idProducto INT NOT NULL,
    tipoAlerta ENUM('STOCK_MINIMO', 'STOCK_AGOTADO') NOT NULL,
    cantidadActual INT NOT NULL,
    stockReferencia INT NOT NULL,
    estado ENUM('PENDIENTE', 'LEIDA') NOT NULL DEFAULT 'PENDIENTE',
    fechaCreacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fechaLeida DATETIME NULL,
    FOREIGN KEY (idUbicacion) REFERENCES ubicacion(idUbicacion),
    FOREIGN KEY (idProducto) REFERENCES producto(idProducto)
) ENGINE=InnoDB;

-- ============================================================================
-- MÓDULO 10: CATEGORÍAS DE PRODUCTOS (NUEVO — wizard crea "General")
-- ============================================================================

CREATE TABLE categoria (
    idCategoria INT AUTO_INCREMENT PRIMARY KEY,
    idEmpresa INT NOT NULL,
    nombreCategoria VARCHAR(100) NOT NULL,
    descripcion VARCHAR(200) NULL,
    isActivo BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (idEmpresa) REFERENCES empresa(idEmpresa)
) ENGINE=InnoDB;

-- ============================================================================
-- ÍNDICES RECOMENDADOS
-- ============================================================================

CREATE INDEX idx_inventario_ubicacion ON inventarioubicacion(idUbicacion);
CREATE INDEX idx_inventario_producto   ON inventarioubicacion(idProducto);
CREATE INDEX idx_movimiento_producto   ON movimientoinventario(idProducto);
CREATE INDEX idx_movimiento_fecha      ON movimientoinventario(fechaHora);
CREATE INDEX idx_venta_fecha           ON venta(fechaHora);
CREATE INDEX idx_venta_ubicacion       ON venta(idUbicacion);
CREATE INDEX idx_solicitud_estado      ON solicitudreposicion(estado);
CREATE INDEX idx_solicitud_origen      ON solicitudreposicion(idUbicacionOrigen);
CREATE INDEX idx_ordencompra_estado    ON ordencompra(estado);
CREATE INDEX idx_alerta_ubicacion      ON alertastock(idUbicacion);
CREATE INDEX idx_alerta_estado         ON alertastock(estado);
CREATE INDEX idx_usuario_correo        ON usuario(correoElectronico);
CREATE INDEX idx_producto_codigo       ON producto(codigoBarras);