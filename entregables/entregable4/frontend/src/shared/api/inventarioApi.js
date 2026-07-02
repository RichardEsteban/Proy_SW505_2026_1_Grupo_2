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

export function listarInventario({ idUbicacion, idProducto, soloBajoMinimo = false } = {}) {
  return apiRequest(`/inventario${buildQuery({
    id_ubicacion: idUbicacion,
    id_producto: idProducto,
    solo_bajo_minimo: soloBajoMinimo
  })}`)
}

export function obtenerInventario(idInventario) {
  return apiRequest(`/inventario/${idInventario}`)
}

export function crearStockInicial(payload) {
  return apiRequest('/inventario/stock-inicial', {
    method: 'POST',
    body: payload
  })
}

export function actualizarStockMinimo(idInventario, payload) {
  return apiRequest(`/inventario/${idInventario}/stock-minimo`, {
    method: 'PATCH',
    body: payload
  })
}

export function listarMovimientos({ idUbicacion, idProducto, desde, hasta, limite = 100 } = {}) {
  return apiRequest(`/inventario/movimientos${buildQuery({
    id_ubicacion: idUbicacion,
    id_producto: idProducto,
    desde,
    hasta,
    limite
  })}`)
}

export function registrarMovimiento(payload) {
  return apiRequest('/inventario/movimientos', {
    method: 'POST',
    body: payload
  })
}
