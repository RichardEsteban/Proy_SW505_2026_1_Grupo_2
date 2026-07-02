import { apiRequest } from '@/shared/api/client'

export function listarUbicaciones({ incluirInactivas = false } = {}) {
  const params = new URLSearchParams({ incluir_inactivas: String(incluirInactivas) })
  return apiRequest(`/ubicaciones?${params.toString()}`)
}

export function obtenerUbicacion(idUbicacion) {
  return apiRequest(`/ubicaciones/${idUbicacion}`)
}

export function crearUbicacion(payload) {
  return apiRequest('/ubicaciones', {
    method: 'POST',
    body: payload
  })
}

export function actualizarUbicacion(idUbicacion, payload) {
  return apiRequest(`/ubicaciones/${idUbicacion}`, {
    method: 'PATCH',
    body: payload
  })
}
