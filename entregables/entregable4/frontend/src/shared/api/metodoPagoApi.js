import { apiRequest } from '@/shared/api/client'

export function listarMetodosPago({ incluirInactivos = false } = {}) {
  const params = new URLSearchParams({ incluir_inactivos: String(incluirInactivos) })
  return apiRequest(`/metodos-pago?${params.toString()}`)
}
