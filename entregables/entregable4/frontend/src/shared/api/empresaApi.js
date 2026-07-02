import { apiRequest } from '@/shared/api/client'

export function obtenerEmpresa() {
  return apiRequest('/empresa')
}

export function actualizarEmpresa(payload) {
  return apiRequest('/empresa', {
    method: 'PUT',
    body: payload
  })
}
