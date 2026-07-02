import { apiRequest } from '@/shared/api/client'

export function listarCategorias({ incluirInactivas = true } = {}) {
  const params = new URLSearchParams({ incluir_inactivas: String(incluirInactivas) })
  return apiRequest(`/categorias?${params.toString()}`)
}

export function obtenerCategoria(idCategoria) {
  return apiRequest(`/categorias/${idCategoria}`)
}

export function crearCategoria(payload) {
  return apiRequest('/categorias', {
    method: 'POST',
    body: payload
  })
}

export function actualizarCategoria(idCategoria, payload) {
  return apiRequest(`/categorias/${idCategoria}`, {
    method: 'PATCH',
    body: payload
  })
}
