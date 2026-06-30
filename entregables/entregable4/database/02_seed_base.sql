USE sistemamype;

INSERT INTO empresa (
    nombreEmpresa,
    isInicializado,
    fechaInicializacion,
    timer_revision_minutos,
    igv_porcentaje,
    moneda
)
SELECT
    'Minimarket Demo SAC',
    TRUE,
    NOW(),
    60,
    18.00,
    'PEN'
WHERE NOT EXISTS (
    SELECT 1
    FROM empresa
    WHERE nombreEmpresa = 'Minimarket Demo SAC'
);

SET @idEmpresa = (
    SELECT idEmpresa
    FROM empresa
    WHERE nombreEmpresa = 'Minimarket Demo SAC'
    LIMIT 1
);

INSERT INTO ubicacion (
    idEmpresa,
    nombreUbicacion,
    tipoUbicacion,
    direccion,
    isActivo
)
SELECT
    @idEmpresa,
    'Almacén Central',
    'ALMACEN',
    'Av. Principal 123 - Lima',
    TRUE
WHERE NOT EXISTS (
    SELECT 1
    FROM ubicacion
    WHERE idEmpresa = @idEmpresa
    AND nombreUbicacion = 'Almacén Central'
);

INSERT INTO ubicacion (
    idEmpresa,
    nombreUbicacion,
    tipoUbicacion,
    direccion,
    isActivo
)
SELECT
    @idEmpresa,
    'Sucursal Surco',
    'SUCURSAL',
    'Av. Caminos del Inca 456 - Surco',
    TRUE
WHERE NOT EXISTS (
    SELECT 1
    FROM ubicacion
    WHERE idEmpresa = @idEmpresa
    AND nombreUbicacion = 'Sucursal Surco'
);

INSERT INTO ubicacion (
    idEmpresa,
    nombreUbicacion,
    tipoUbicacion,
    direccion,
    isActivo
)
SELECT
    @idEmpresa,
    'Sucursal Miraflores',
    'SUCURSAL',
    'Av. Larco 789 - Miraflores',
    TRUE
WHERE NOT EXISTS (
    SELECT 1
    FROM ubicacion
    WHERE idEmpresa = @idEmpresa
    AND nombreUbicacion = 'Sucursal Miraflores'
);

INSERT IGNORE INTO rol (nombreRol) VALUES
('ADMIN'),
('VENDEDOR'),
('SUPERVISOR_SUCURSAL'),
('SUPERVISOR_ALMACEN');