# Administrador General

Esta carpeta contiene solo las pantallas propias del rol **Administrador General** según los casos de uso aprobados.

## Pantallas principales

- `DashboardPage.jsx`
- `AdministracionPage.jsx` → usuarios, empleados, roles y estado de acceso.
- `ProductosPage.jsx`
- `CategoriasPage.jsx`
- `ProveedoresPage.jsx`
- `OrdenesCompraPage.jsx` → creación de órdenes de compra para proveedores.
- `UbicacionesPage.jsx` → almacén central y sucursales en una sola vista.
- `ReportesPage.jsx`

## Cambios para evitar código muerto

Las vistas administrativas que no pertenecían a los casos de uso actuales del Administrador General fueron retiradas de esta carpeta y de las rutas de admin:

- `AlmacenCentralPage.jsx`
- `SucursalesPage.jsx`
- `TransferenciasPage.jsx`
- `ComprasPage.jsx`
- `VentasPage.jsx`
- `MovimientosPage.jsx`
- `ConfiguracionPage.jsx`
- `ClientesPage.jsx`

Esas responsabilidades quedan en los roles operativos correspondientes o dentro de reportes, no como pantallas independientes del Administrador General.

## Regla de trabajo del equipo

- La persona asignada a este rol debe modificar principalmente archivos dentro de esta carpeta.
- Los componentes, APIs y utilidades compartidas están en `src/shared`.
- No modificar carpetas de otros roles salvo coordinación previa.
