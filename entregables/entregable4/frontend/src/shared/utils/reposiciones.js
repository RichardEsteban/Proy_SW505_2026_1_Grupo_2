import { ROLES } from '@/shared/utils/roles'

export const ESTADOS_REPOSICION = {
  ENVIADO: 'ENVIADO',
  EN_REVISION: 'EN_REVISION',
  ACEPTADO: 'ACEPTADO',
  EN_TRANSITO: 'EN_TRANSITO',
  RECIBIDA: 'RECIBIDA',
  RECHAZADA: 'RECHAZADA',
  CANCELADA: 'CANCELADA'
}

export const ESTADO_REPOSICION_LABELS = {
  [ESTADOS_REPOSICION.ENVIADO]: 'Enviado',
  [ESTADOS_REPOSICION.EN_REVISION]: 'En revisión',
  [ESTADOS_REPOSICION.ACEPTADO]: 'Aceptado',
  [ESTADOS_REPOSICION.EN_TRANSITO]: 'En tránsito',
  [ESTADOS_REPOSICION.RECIBIDA]: 'Recibida',
  [ESTADOS_REPOSICION.RECHAZADA]: 'Rechazada',
  [ESTADOS_REPOSICION.CANCELADA]: 'Cancelada'
}

export function formatEstadoReposicion(estado) {
  return ESTADO_REPOSICION_LABELS[estado] || estado || '-'
}

export function getEstadoReposicionTone(estado) {
  const tones = {
    [ESTADOS_REPOSICION.ENVIADO]: 'amber',
    [ESTADOS_REPOSICION.EN_REVISION]: 'slate',
    [ESTADOS_REPOSICION.ACEPTADO]: 'green',
    [ESTADOS_REPOSICION.EN_TRANSITO]: 'slate',
    [ESTADOS_REPOSICION.RECIBIDA]: 'green',
    [ESTADOS_REPOSICION.RECHAZADA]: 'red',
    [ESTADOS_REPOSICION.CANCELADA]: 'red'
  }

  return tones[estado] || 'slate'
}

export function formatDateTime(value) {
  if (!value) return '-'

  return new Intl.DateTimeFormat('es-PE', {
    dateStyle: 'short',
    timeStyle: 'short'
  }).format(new Date(value))
}

export function toIsoFromLocalDateTime(value) {
  if (!value) return undefined
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? undefined : date.toISOString()
}

export function getApiErrorMessage(error, fallback) {
  if (typeof error?.message === 'string' && error.message.trim()) {
    return error.message
  }

  return fallback
}

export function isCentralRole(role) {
  return [ROLES.ADMIN, ROLES.SUPERVISOR_ALMACEN].includes(role)
}

export function canCreateReposicion(role) {
  return [ROLES.ADMIN, ROLES.SUPERVISOR_ALMACEN, ROLES.SUPERVISOR_SUCURSAL].includes(role)
}

export function canOpenRevision(role) {
  return isCentralRole(role)
}

export function canApproveOrReject(role) {
  return isCentralRole(role)
}

export function canSendReposicion(role) {
  return isCentralRole(role)
}

export function canReceiveReposicion(role) {
  return [ROLES.ADMIN, ROLES.SUPERVISOR_ALMACEN, ROLES.SUPERVISOR_SUCURSAL].includes(role)
}

export function canCancelReposicion(role) {
  return [ROLES.ADMIN, ROLES.SUPERVISOR_ALMACEN, ROLES.SUPERVISOR_SUCURSAL].includes(role)
}

export function summarizeReposiciones(reposiciones) {
  return {
    total: reposiciones.length,
    pendientes: reposiciones.filter((item) => [ESTADOS_REPOSICION.ENVIADO, ESTADOS_REPOSICION.EN_REVISION].includes(item.estado)).length,
    aceptadas: reposiciones.filter((item) => item.estado === ESTADOS_REPOSICION.ACEPTADO).length,
    transito: reposiciones.filter((item) => item.estado === ESTADOS_REPOSICION.EN_TRANSITO).length,
    recibidas: reposiciones.filter((item) => item.estado === ESTADOS_REPOSICION.RECIBIDA).length
  }
}

export function totalSolicitado(solicitud) {
  return (solicitud.detalles || []).reduce((sum, detalle) => sum + Number(detalle.cantidadSolicitada || 0), 0)
}

export function totalDespachado(solicitud) {
  return (solicitud.detalles || []).reduce((sum, detalle) => sum + Number(detalle.cantidadDespachada || 0), 0)
}
