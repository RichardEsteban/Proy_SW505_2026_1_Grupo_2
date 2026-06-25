-- ============================================================
-- SEED DESARROLLO - MySQL 8
-- Datos mínimos para arrancar el sistema
-- ============================================================

-- Roles
INSERT INTO roles (nombre, descripcion, permisos) VALUES
  ('Administrador', 'Acceso total', '["*"]'),
  ('Almacenero', 'Gestiona entradas/transferencias', '["almacen:*"]'),
  ('Vendedor', 'Opera el POS', '["ventas:create","inventario:read"]'),
  ('Supervisor', 'Aprueba solicitudes y reportes', '["reposicion:*","reportes:read"]');

-- Métodos de pago
INSERT INTO metodos_pago (nombre, descripcion) VALUES
  ('Efectivo', 'Pago en efectivo'),
  ('Tarjeta', 'Débito/crédito'),
  ('Yape/Plin', 'Transferencia inmediata'),
  ('Transferencia', 'Transferencia bancaria');

-- Sucursales
INSERT INTO sucursales (codigo, nombre, direccion, telefono) VALUES
  ('S001', 'Sucursal Principal', 'Av. Principal 123', '987654321'),
  ('S002', 'Sucursal Norte', 'Av. Norte 456', '987654322');

-- Almacenes
INSERT INTO almacenes (codigo, nombre, direccion) VALUES
  ('A001', 'Almacén Central', 'Av. Industrial 789'),
  ('A002', 'Almacén Norte', 'Av. Norte 456');

-- Categorías
INSERT INTO categorias (nombre, descripcion) VALUES
  ('Bebidas', 'Gaseosas, jugos, aguas'),
  ('Abarrotes', 'Productos de consumo masivo'),
  ('Limpieza', 'Productos de limpieza');

-- Proveedores demo
INSERT INTO proveedores (ruc, razon_social, nombre_comercial, telefono, email) VALUES
  ('20123456789', 'Distribuidora ABC S.A.C.', 'ABC', '987111222', 'contacto@abc.com'),
  ('20987654321', 'Comercial XYZ E.I.R.L.', 'XYZ', '987333444', 'ventas@xyz.com');

-- Productos demo
INSERT INTO productos (sku, codigo_barra, nombre, descripcion, categoria_id, proveedor_id, precio_compra, precio_venta, unidad_medida) VALUES
  ('P0001', '7750001000011', 'Gaseosa Cola 500ml', 'Botella personal', 1, 1, 1.20, 2.50, 'UND'),
  ('P0002', '7750001000028', 'Agua Mineral 600ml', 'Sin gas', 1, 1, 0.50, 1.50, 'UND'),
  ('P0003', '7750001000035', 'Arroz Costeño 1kg', 'Arroz superior', 2, 2, 3.00, 4.50, 'KG'),
  ('P0004', '7750001000042', 'Azúcar Blanca 1kg', 'Azúcar refinada', 2, 2, 2.50, 3.80, 'KG'),
  ('P0005', '7750001000059', 'Detergente 1kg', 'Rinde 20 lavadas', 3, 1, 5.00, 8.50, 'UND');

-- Stock inicial
INSERT INTO stock (producto_id, ubicacion_tipo, ubicacion_id, cantidad, stock_minimo) VALUES
  (1, 'SUCURSAL', 1, 50, 10),
  (2, 'SUCURSAL', 1, 80, 15),
  (3, 'SUCURSAL', 1, 30, 5),
  (4, 'SUCURSAL', 1, 25, 5),
  (5, 'SUCURSAL', 1, 15, 3),
  (1, 'ALMACEN', 1, 200, 50),
  (2, 'ALMACEN', 1, 300, 80),
  (3, 'ALMACEN', 1, 150, 30);

-- Clientes demo
INSERT INTO clientes (tipo_documento, numero_documento, nombre, direccion) VALUES
  ('DNI', '12345678', 'Cliente Varios', '-'),
  ('RUC', '20123456789', 'Empresa Demo S.A.C.', 'Av. Demo 123');

-- NOTA: El usuario admin se crea con password hasheada desde Python
-- al arrancar el backend, usando bcrypt. Aquí dejamos un placeholder
-- que se sobreescribe en el primer arranque con el script init_admin.py
-- (o usando el endpoint /api/auth/wizard-inicial desde el frontend).
