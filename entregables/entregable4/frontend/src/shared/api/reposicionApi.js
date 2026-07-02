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

export function listarReposiciones({ idUbicacionOrigen, idUbicacionDestino, estado, desde, hasta, limite = 100 } = {}) {
  return apiRequest(`/reposiciones${buildQuery({
    id_ubicacion_origen: idUbicacionOrigen,
    id_ubicacion_destino: idUbicacionDestino,
    estado,
    desde,
    hasta,
    limite
  })}`)
}

export function obtenerReposicion(idSolicitud) {
  return apiRequest(`/reposiciones/${idSolicitud}`)
}

export function crearReposicion(payload) {
  return apiRequest('/reposiciones', {
    method: 'POST',
    body: payload
  })
}

export function editarReposicion(idSolicitud, payload) {
  return apiRequest(`/reposiciones/${idSolicitud}/editar`, {
    method: 'PATCH',
    body: payload
  })
}

function buildGestionBody(observacion = '') {
  return observacion?.trim() ? { observacion: observacion.trim() } : {}
}

export function abrirRevisionReposicion(idSolicitud, observacion = '') {
  return apiRequest(`/reposiciones/${idSolicitud}/abrir-revision`, {
    method: 'PATCH',
    body: buildGestionBody(observacion)
  })
}

export function aprobarReposicion(idSolicitud, observacion = '') {
  return apiRequest(`/reposiciones/${idSolicitud}/aprobar`, {
    method: 'PATCH',
    body: buildGestionBody(observacion)
  })
}

export function rechazarReposicion(idSolicitud, observacion = '') {
  return apiRequest(`/reposiciones/${idSolicitud}/rechazar`, {
    method: 'PATCH',
    body: buildGestionBody(observacion)
  })
}

export function enviarReposicion(idSolicitud, observacion = '') {
  return apiRequest(`/reposiciones/${idSolicitud}/enviar`, {
    method: 'PATCH',
    body: buildGestionBody(observacion)
  })
}

export function recibirReposicion(idSolicitud, observacion = '') {
  return apiRequest(`/reposiciones/${idSolicitud}/recibir`, {
    method: 'PATCH',
    body: buildGestionBody(observacion)
  })
}

export function cancelarReposicion(idSolicitud, observacion = '') {
  return apiRequest(`/reposiciones/${idSolicitud}/cancelar`, {
    method: 'PATCH',
    body: buildGestionBody(observacion)
  })
}
