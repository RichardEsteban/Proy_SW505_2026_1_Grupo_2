import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '@shared/hooks/useAuth.js';

import Navbar from '@shared/components/Navbar.jsx';
import ProtectedRoute from '@shared/components/ProtectedRoute.jsx';

import Login from '@modules/auth/pages/Login.jsx';
import CambiarPassword from '@modules/auth/pages/CambiarPassword.jsx';
import RecuperarPassword from '@modules/auth/pages/RecuperarPassword.jsx';
import Wizard from '@modules/auth/pages/Wizard.jsx';

import POS from '@modules/ventas/pages/POS.jsx';
import InventarioSucursal from '@modules/inventario/pages/InventarioSucursal.jsx';
import SolicitudesRepo from '@modules/reposicion/pages/Solicitudes.jsx';
import Recepcion from '@modules/reposicion/pages/Recepcion.jsx';
import Almacen from '@modules/almacen/pages/Almacen.jsx';
import Entradas from '@modules/almacen/pages/Entradas.jsx';
import SolicitudesAlmacen from '@modules/almacen/pages/Solicitudes.jsx';
import Movimientos from '@modules/almacen/pages/Movimientos.jsx';
import DashboardAlmacen from '@modules/almacen/pages/DashboardAlmacen.jsx';
import Dashboard from '@modules/admin/pages/Dashboard.jsx';
import Empleados from '@modules/admin/pages/Empleados.jsx';
import Productos from '@modules/admin/pages/Productos.jsx';
import Ubicaciones from '@modules/admin/pages/Ubicaciones.jsx';
import MetodosPago from '@modules/admin/pages/MetodosPago.jsx';
import Roles from '@modules/admin/pages/Roles.jsx';
import Clientes from '@modules/admin/pages/Clientes.jsx';
import Proveedores from '@modules/admin/pages/Proveedores.jsx';
import Reportes from '@modules/admin/pages/Reportes.jsx';
import DashboardSucursal from '@modules/sucursal/pages/DashboardSucursal.jsx';

function Layout({ children }) {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1 max-w-7xl w-full mx-auto p-4">{children}</main>
    </div>
  );
}

export default function AppRouter() {
  const { user } = useAuth();
  return (
    <Routes>
      {/* Públicas */}
      <Route path="/login" element={<Login />} />
      <Route path="/recuperar-password" element={<RecuperarPassword />} />
      <Route path="/wizard" element={<Wizard />} />
      <Route path="/cambiar-password" element={<ProtectedRoute><CambiarPassword /></ProtectedRoute>} />

      {/* Protegidas con layout */}
      <Route path="/" element={<ProtectedRoute><Layout><HomeRedirect /></Layout></ProtectedRoute>} />
      <Route path="/pos" element={<ProtectedRoute roles={['2', '3', '1']}><Layout><POS /></Layout></ProtectedRoute>} />
      <Route path="/inventario" element={<ProtectedRoute><Layout><InventarioSucursal /></Layout></ProtectedRoute>} />
      <Route path="/reposicion" element={<ProtectedRoute><Layout><SolicitudesRepo /></Layout></ProtectedRoute>} />
      <Route path="/reposicion/recepcion" element={<ProtectedRoute><Layout><Recepcion /></Layout></ProtectedRoute>} />

      <Route path="/almacen" element={<ProtectedRoute><Layout><DashboardAlmacen /></Layout></ProtectedRoute>} />
      <Route path="/almacen/entradas" element={<ProtectedRoute><Layout><Entradas /></Layout></ProtectedRoute>} />
      <Route path="/almacen/solicitudes" element={<ProtectedRoute><Layout><SolicitudesAlmacen /></Layout></ProtectedRoute>} />
      <Route path="/almacen/movimientos" element={<ProtectedRoute><Layout><Movimientos /></Layout></ProtectedRoute>} />
      <Route path="/almacen/registro" element={<ProtectedRoute><Layout><Almacen /></Layout></ProtectedRoute>} />

      <Route path="/admin" element={<ProtectedRoute roles={['1']}><Layout><Dashboard /></Layout></ProtectedRoute>} />
      <Route path="/admin/empleados" element={<ProtectedRoute roles={['1']}><Layout><Empleados /></Layout></ProtectedRoute>} />
      <Route path="/admin/productos" element={<ProtectedRoute roles={['1']}><Layout><Productos /></Layout></ProtectedRoute>} />
      <Route path="/admin/ubicaciones" element={<ProtectedRoute roles={['1']}><Layout><Ubicaciones /></Layout></ProtectedRoute>} />
      <Route path="/admin/metodos-pago" element={<ProtectedRoute roles={['1']}><Layout><MetodosPago /></Layout></ProtectedRoute>} />
      <Route path="/admin/roles" element={<ProtectedRoute roles={['1']}><Layout><Roles /></Layout></ProtectedRoute>} />
      <Route path="/admin/clientes" element={<ProtectedRoute><Layout><Clientes /></Layout></ProtectedRoute>} />
      <Route path="/admin/proveedores" element={<ProtectedRoute><Layout><Proveedores /></Layout></ProtectedRoute>} />
      <Route path="/admin/reportes" element={<ProtectedRoute roles={['1']}><Layout><Reportes /></Layout></ProtectedRoute>} />

      <Route path="/reportes" element={<ProtectedRoute><Layout><Reportes /></Layout></ProtectedRoute>} />
      <Route path="/sucursal" element={<ProtectedRoute><Layout><DashboardSucursal /></Layout></ProtectedRoute>} />

      <Route path="*" element={<Navigate to={user ? '/' : '/login'} replace />} />
    </Routes>
  );
}

function HomeRedirect() {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  // Redirige según rol
  if (user.rol === '1') return <Navigate to="/admin" replace />;
  if (user.rol === '3') return <Navigate to="/pos" replace />;
  if (user.rol === '2') return <Navigate to="/almacen" replace />;
  return <Navigate to="/inventario" replace />;
}
