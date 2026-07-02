import { Navigate } from 'react-router-dom'
import Loader from '@/shared/components/Loader'
import { useAuth } from './AuthContext'
import { getDefaultPathForRole } from '@/shared/utils/roleViews'

export default function RoleHomeRedirect() {
  const { usuario, loading, isAuthenticated } = useAuth()

  if (loading) return <Loader message="Preparando tu vista..." />
  if (!isAuthenticated) return <Navigate to="/login" replace />

  return <Navigate to={getDefaultPathForRole(usuario?.rol)} replace />
}
