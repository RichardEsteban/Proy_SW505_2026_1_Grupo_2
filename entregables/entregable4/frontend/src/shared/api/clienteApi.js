import { apiRequest } from '@/shared/api/client'

export function listarClientes({ incluirInactivos = false } = {}) {
  const params = new URLSearchParams({ incluir_inactivos: String(incluirInactivos) })
  return apiRequest(`/clientes?${params.toString()}`)
}

export function obtenerCliente(idCliente) {
  return apiRequest(`/clientes/${idCliente}`)
}

export function crearCliente(payload) {
  return apiRequest('/clientes', {
    method: 'POST',
    body: payload
  })
}

export function actualizarCliente(idCliente, payload) {
  return apiRequest(`/clientes/${idCliente}`, {
    method: 'PATCH',
    body: payload
  })
}
