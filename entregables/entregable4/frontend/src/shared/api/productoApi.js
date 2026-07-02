import { apiRequest } from '@/shared/api/client'

export function listarProductos({ incluirInactivos = true } = {}) {
  const params = new URLSearchParams({ incluir_inactivos: String(incluirInactivos) })
  return apiRequest(`/productos?${params.toString()}`)
}

export function obtenerProducto(idProducto) {
  return apiRequest(`/productos/${idProducto}`)
}

export function obtenerProductoPorCodigo(codigoBarras) {
  return apiRequest(`/productos/codigo/${encodeURIComponent(codigoBarras)}`)
}

export function crearProducto(payload) {
  return apiRequest('/productos', {
    method: 'POST',
    body: payload
  })
}

export function actualizarProducto(idProducto, payload) {
  return apiRequest(`/productos/${idProducto}`, {
    method: 'PATCH',
    body: payload
  })
}
