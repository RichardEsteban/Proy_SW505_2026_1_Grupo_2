import { apiRequest } from '@/shared/api/client'

function buildQuery(params = {}) {
  const query = new URLSearchParams()

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      query.set(key, String(value))
    }
  })

  const queryString = query.toString()
  return queryString ? `?${queryString}` : ''
}

export function listarVentas({ idUbicacion, idUsuario, desde, hasta, limite = 100 } = {}) {
  return apiRequest(`/ventas${buildQuery({
    id_ubicacion: idUbicacion,
    id_usuario: idUsuario,
    desde,
    hasta,
    limite
  })}`)
}

export function obtenerVenta(idVenta) {
  return apiRequest(`/ventas/${idVenta}`)
}

export function crearVenta(payload) {
  return apiRequest('/ventas', {
    method: 'POST',
    body: payload
  })
}
