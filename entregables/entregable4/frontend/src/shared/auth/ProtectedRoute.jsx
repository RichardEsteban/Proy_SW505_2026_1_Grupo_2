import { Navigate, Outlet, useLocation } from 'react-router-dom'
import Loader from '@/shared/components/Loader'
import { useAuth } from './AuthContext'

export default function ProtectedRoute() {
  const { isAuthenticated, loading } = useAuth()
  const location = useLocation()

  if (loading) {
    return <Loader message="Verificando sesión..." />
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />
  }

  return <Outlet />
}
