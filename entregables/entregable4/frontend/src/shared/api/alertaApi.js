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

export function listarAlertas({ idUbicacion, estado = 'PENDIENTE' } = {}) {
  return apiRequest(`/alertas${buildQuery({
    id_ubicacion: idUbicacion,
    estado
  })}`)
}

export function marcarAlertaComoLeida(idAlerta) {
  return apiRequest(`/alertas/${idAlerta}/leer`, {
    method: 'PATCH'
  })
}
