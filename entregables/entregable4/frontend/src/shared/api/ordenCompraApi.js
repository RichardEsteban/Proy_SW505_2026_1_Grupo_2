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

export function listarOrdenesCompra({ idProveedor, idUbicacionDestino, estado, desde, hasta, limite = 100 } = {}) {
  return apiRequest(`/ordenes-compra${buildQuery({
    id_proveedor: idProveedor,
    id_ubicacion_destino: idUbicacionDestino,
    estado,
    desde,
    hasta,
    limite
  })}`)
}

export function obtenerOrdenCompra(idOrdenCompra) {
  return apiRequest(`/ordenes-compra/${idOrdenCompra}`)
}

export function crearOrdenCompra(payload) {
  return apiRequest('/ordenes-compra', {
    method: 'POST',
    body: payload
  })
}

export function enviarOrdenCompra(idOrdenCompra) {
  return apiRequest(`/ordenes-compra/${idOrdenCompra}/enviar`, {
    method: 'PATCH'
  })
}

export function recibirOrdenCompra(idOrdenCompra) {
  return apiRequest(`/ordenes-compra/${idOrdenCompra}/recibir`, {
    method: 'PATCH'
  })
}

export function cancelarOrdenCompra(idOrdenCompra, motivo = '') {
  return apiRequest(`/ordenes-compra/${idOrdenCompra}/cancelar`, {
    method: 'PATCH',
    body: motivo ? { motivo } : {}
  })
}
