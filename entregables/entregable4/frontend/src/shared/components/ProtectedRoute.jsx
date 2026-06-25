import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@shared/hooks/useAuth.js';

/**
 * Protege rutas por autenticación + roles permitidos.
 * Uso: <ProtectedRoute roles={['1']}><Dashboard /></ProtectedRoute>
 */
export default function ProtectedRoute({ children, roles = null }) {
  const { user, token } = useAuth();
  const location = useLocation();

  if (!token || !user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  if (user.debe_cambiar_password && !location.pathname.startsWith('/cambiar-password')) {
    return <Navigate to="/cambiar-password" replace />;
  }
  if (roles && !roles.includes(String(user.rol))) {
    return <Navigate to="/" replace />;
  }
  return children;
}
