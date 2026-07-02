import { Navigate } from 'react-router-dom'
import Loader from '@/shared/components/Loader'
import { useAuth } from '@/shared/auth/AuthContext'
import { getDefaultPathForRole } from '@/shared/utils/roleViews'

export default function RolePage({ pagesByRole = {} }) {
  const { usuario, loading, isAuthenticated } = useAuth()

  if (loading) return <Loader message="Preparando vista por rol..." />
  if (!isAuthenticated) return <Navigate to="/login" replace />

  const Page = pagesByRole[usuario?.rol]

  if (!Page) {
    return <Navigate to={getDefaultPathForRole(usuario?.rol)} replace />
  }

  return <Page />
}
