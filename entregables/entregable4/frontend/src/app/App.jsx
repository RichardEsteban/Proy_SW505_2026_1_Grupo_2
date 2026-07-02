import { Route, Routes } from 'react-router-dom'
import ProtectedRoute from '@/shared/auth/ProtectedRoute'
import RequireRole from '@/shared/auth/RequireRole'
import RoleHomeRedirect from '@/shared/auth/RoleHomeRedirect'
import RolePage from '@/app/routing/RolePage'
import LoginPage from '@/shared/pages/auth/LoginPage'
import RecuperarContrasenaPage from '@/shared/pages/auth/RecuperarContrasenaPage'
import NotFoundPage from '@/shared/pages/system/NotFoundPage'
import MainLayout from '@/app/layouts/MainLayout'
import { ROLES } from '@/shared/utils/roles'

// Administrador General
import AdminDashboardPage from '@/roles/administrador-general/pages/DashboardPage'
import AdminAdministracionPage from '@/roles/administrador-general/pages/AdministracionPage'
import AdminProductosPage from '@/roles/administrador-general/pages/ProductosPage'
import AdminCategoriasPage from '@/roles/administrador-general/pages/CategoriasPage'
import AdminProveedoresPage from '@/roles/administrador-general/pages/ProveedoresPage'
import AdminOrdenesCompraPage from '@/roles/administrador-general/pages/OrdenesCompraPage'
import AdminUbicacionesPage from '@/roles/administrador-general/pages/UbicacionesPage'
import AdminReportesPage from '@/roles/administrador-general/pages/ReportesPage'

// Supervisor de Almacén Central
import AlmacenDashboardPage from '@/roles/encargado-almacen-central/pages/DashboardPage'
import AlmacenInventarioPage from '@/roles/encargado-almacen-central/pages/InventarioPage'
import AlmacenSucursalesPage from '@/roles/encargado-almacen-central/pages/SucursalesPage'
import AlmacenRecepcionesPage from '@/roles/encargado-almacen-central/pages/RecepcionesPage'
import AlmacenSolicitudesReposicionPage from '@/roles/encargado-almacen-central/pages/SolicitudesReposicionPage'
import AlmacenDespachosPage from '@/roles/encargado-almacen-central/pages/DespachosPage'
import AlmacenMovimientosPage from '@/roles/encargado-almacen-central/pages/MovimientosPage'

// Supervisor de Sucursal
import SucursalDashboardPage from '@/roles/supervisor-sucursal/pages/DashboardPage'
import SucursalInventarioPage from '@/roles/supervisor-sucursal/pages/InventarioPage'
import SucursalSolicitudesReposicionPage from '@/roles/supervisor-sucursal/pages/SolicitudesReposicionPage'
import SucursalRecepcionesPage from '@/roles/supervisor-sucursal/pages/RecepcionesPage'
import SucursalMovimientosPage from '@/roles/supervisor-sucursal/pages/MovimientosPage'
import SucursalAlertasStockPage from '@/roles/supervisor-sucursal/pages/AlertasStockPage'

// Vendedor
import VendedorInventarioPage from '@/roles/vendedor/pages/InventarioPage'
import VendedorVentasPage from '@/roles/vendedor/pages/VentasPage'

function withRole(element, allowedRoles) {
  return <RequireRole allowedRoles={allowedRoles}>{element}</RequireRole>
}

export default function App() {
  const admin = [ROLES.ADMIN]
  const almacen = [ROLES.SUPERVISOR_ALMACEN]
  const sucursal = [ROLES.SUPERVISOR_SUCURSAL]
  const reportes = [ROLES.ADMIN]
  const movimientos = [ROLES.SUPERVISOR_ALMACEN, ROLES.SUPERVISOR_SUCURSAL]
  const dashboard = [ROLES.ADMIN, ROLES.SUPERVISOR_ALMACEN, ROLES.SUPERVISOR_SUCURSAL]

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/recuperar-contrasena" element={<RecuperarContrasenaPage />} />

      <Route element={<ProtectedRoute />}>
        <Route path="/" element={<RoleHomeRedirect />} />
        <Route element={<MainLayout />}>
          <Route
            path="/dashboard"
            element={withRole(
              <RolePage
                pagesByRole={{
                  [ROLES.ADMIN]: AdminDashboardPage,
                  [ROLES.SUPERVISOR_ALMACEN]: AlmacenDashboardPage,
                  [ROLES.SUPERVISOR_SUCURSAL]: SucursalDashboardPage
                }}
              />,
              dashboard
            )}
          />

          {/* Administrador General */}
          <Route path="/usuarios" element={withRole(<AdminAdministracionPage />, admin)} />
          <Route path="/productos" element={withRole(<AdminProductosPage />, admin)} />
          <Route path="/categorias" element={withRole(<AdminCategoriasPage />, admin)} />
          <Route path="/proveedores" element={withRole(<AdminProveedoresPage />, admin)} />
          <Route path="/ordenes-compra" element={withRole(<AdminOrdenesCompraPage />, admin)} />
          <Route path="/ubicaciones" element={withRole(<AdminUbicacionesPage />, admin)} />

          {/* Supervisor de Almacén Central */}
          <Route path="/sucursales" element={withRole(<AlmacenSucursalesPage />, almacen)} />
          <Route
            path="/solicitudes-reposicion"
            element={withRole(
              <RolePage
                pagesByRole={{
                  [ROLES.SUPERVISOR_ALMACEN]: AlmacenSolicitudesReposicionPage,
                  [ROLES.SUPERVISOR_SUCURSAL]: SucursalSolicitudesReposicionPage
                }}
              />,
              [ROLES.SUPERVISOR_ALMACEN, ROLES.SUPERVISOR_SUCURSAL]
            )}
          />
          <Route path="/despachos" element={withRole(<AlmacenDespachosPage />, almacen)} />

          {/* Supervisor de Sucursal */}
          <Route path="/alertas-stock" element={withRole(<SucursalAlertasStockPage />, sucursal)} />

          <Route
            path="/recepciones"
            element={withRole(
              <RolePage
                pagesByRole={{
                  [ROLES.SUPERVISOR_ALMACEN]: AlmacenRecepcionesPage,
                  [ROLES.SUPERVISOR_SUCURSAL]: SucursalRecepcionesPage
                }}
              />,
              [ROLES.SUPERVISOR_ALMACEN, ROLES.SUPERVISOR_SUCURSAL]
            )}
          />

          {/* Inventario separado por rol */}
          <Route
            path="/inventario"
            element={withRole(
              <RolePage
                pagesByRole={{
                  [ROLES.SUPERVISOR_ALMACEN]: AlmacenInventarioPage,
                  [ROLES.SUPERVISOR_SUCURSAL]: SucursalInventarioPage,
                  [ROLES.VENDEDOR]: VendedorInventarioPage
                }}
              />,
              [ROLES.SUPERVISOR_ALMACEN, ROLES.SUPERVISOR_SUCURSAL, ROLES.VENDEDOR]
            )}
          />
          <Route path="/ventas" element={withRole(<VendedorVentasPage />, [ROLES.VENDEDOR])} />

          {/* Compartidas, pero con archivo separado por rol */}
          <Route
            path="/movimientos"
            element={withRole(
              <RolePage
                pagesByRole={{
                  [ROLES.SUPERVISOR_ALMACEN]: AlmacenMovimientosPage,
                  [ROLES.SUPERVISOR_SUCURSAL]: SucursalMovimientosPage
                }}
              />,
              movimientos
            )}
          />
          <Route path="/reportes" element={withRole(<AdminReportesPage />, reportes)} />
        </Route>
      </Route>

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  )
}
