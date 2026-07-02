import { ROLES } from '@/shared/utils/roles'

export const TIPOS_MOVIMIENTO = ['INGRESO', 'SALIDA']

export const MOTIVOS_MOVIMIENTO = [
  'AJUSTE',
  'MERMA',
  'VENTA',
  'COMPRA_PROVEEDOR',
  'REPOSICION_ENVIADA',
  'REPOSICION_RECIBIDA'
]

export function canCreateStock(role) {
  return [ROLES.ADMIN, ROLES.SUPERVISOR_ALMACEN].includes(role)
}

export function canRegisterMovement(role) {
  return [ROLES.ADMIN, ROLES.SUPERVISOR_ALMACEN].includes(role)
}

export function canUpdateStockMinimo(role) {
  return [ROLES.ADMIN, ROLES.SUPERVISOR_ALMACEN, ROLES.SUPERVISOR_SUCURSAL].includes(role)
}

export function getStockBadgeTone(estadoStock) {
  if (estadoStock === 'STOCK_AGOTADO') return 'red'
  if (estadoStock === 'STOCK_MINIMO') return 'amber'
  return 'green'
}

export function getAlertBadgeTone(tipoAlerta) {
  return tipoAlerta === 'STOCK_AGOTADO' ? 'red' : 'amber'
}

export function formatDateTime(value) {
  if (!value) return '-'

  return new Intl.DateTimeFormat('es-PE', {
    dateStyle: 'short',
    timeStyle: 'short'
  }).format(new Date(value))
}

export function getApiErrorMessage(error, fallback = 'No se pudo completar la operación') {
  if (!error) return fallback

  if (Array.isArray(error.data?.detail)) {
    return error.data.detail.map((item) => item.msg).join('. ')
  }

  if (typeof error.message === 'string' && error.message) {
    return error.message
  }

  return fallback
}
