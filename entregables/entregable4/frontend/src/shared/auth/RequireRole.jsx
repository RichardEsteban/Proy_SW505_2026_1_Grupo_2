import { Navigate } from 'react-router-dom'
import Loader from '@/shared/components/Loader'
import { useAuth } from './AuthContext'
import { getDefaultPathForRole } from '@/shared/utils/roleViews'

export default function RequireRole({ allowedRoles = [], children }) {
  const { usuario, loading, isAuthenticated } = useAuth()

  if (loading) return <Loader message="Validando permisos..." />
  if (!isAuthenticated) return <Navigate to="/login" replace />

  if (allowedRoles.length > 0 && !allowedRoles.includes(usuario?.rol)) {
    return <Navigate to={getDefaultPathForRole(usuario?.rol)} replace />
  }

  return children
}
