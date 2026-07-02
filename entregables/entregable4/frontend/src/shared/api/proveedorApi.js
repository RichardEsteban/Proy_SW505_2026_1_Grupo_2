import { apiRequest } from '@/shared/api/client'

export function listarProveedores({ incluirInactivos = true } = {}) {
  const params = new URLSearchParams({ incluir_inactivos: String(incluirInactivos) })
  return apiRequest(`/proveedores?${params.toString()}`)
}

export function obtenerProveedor(idProveedor) {
  return apiRequest(`/proveedores/${idProveedor}`)
}

export function crearProveedor(payload) {
  return apiRequest('/proveedores', {
    method: 'POST',
    body: payload
  })
}

export function actualizarProveedor(idProveedor, payload) {
  return apiRequest(`/proveedores/${idProveedor}`, {
    method: 'PATCH',
    body: payload
  })
}
