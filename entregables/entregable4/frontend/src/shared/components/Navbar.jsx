import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '@shared/hooks/useAuth.js';
import AlertaStock from '@shared/components/AlertaStock.jsx';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center gap-8">
            <Link to="/" className="flex items-center gap-2 font-bold text-xl text-primary-700">
              <span>📦</span> Sistema Inventario
            </Link>
            <nav className="hidden md:flex items-center gap-1">
              <NavItem to="/pos">POS</NavItem>
              <NavItem to="/inventario">Inventario</NavItem>
              <NavItem to="/reposicion">Reposición</NavItem>
              <NavItem to="/almacen">Almacén</NavItem>
              <NavItem to="/admin">Admin</NavItem>
              <NavItem to="/reportes">Reportes</NavItem>
            </nav>
          </div>
          <div className="flex items-center gap-4">
            {user && <AlertaStock sucursalId={user.sucursal_id} />}
            <div className="text-right hidden sm:block">
              <div className="text-sm font-medium">{user?.nombre_completo}</div>
              <div className="text-xs text-gray-500">Rol: {user?.rol}</div>
            </div>
            <button onClick={handleLogout} className="btn-secondary text-sm">
              Salir
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}

function NavItem({ to, children }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `px-3 py-2 rounded-md text-sm font-medium transition ${
          isActive
            ? 'bg-primary-50 text-primary-700'
            : 'text-gray-700 hover:bg-gray-100'
        }`
      }
    >
      {children}
    </NavLink>
  );
}
