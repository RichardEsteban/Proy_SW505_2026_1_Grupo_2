import { ROLES } from '@/shared/utils/roles'

export function canManageCatalog(role) {
  return [ROLES.ADMIN, ROLES.SUPERVISOR_ALMACEN].includes(role)
}

export function formatBooleanStatus(value) {
  return value ? 'Activo' : 'Inactivo'
}

export function normalizeDecimal(value) {
  if (value === '' || value === null || value === undefined) return ''
  const number = Number(value)
  return Number.isNaN(number) ? '' : number.toFixed(2)
}

export function getApiErrorMessage(error, fallback = 'No se pudo completar la operación') {
  if (!error) return fallback

  if (typeof error.message === 'string' && error.message) {
    return error.message
  }

  if (Array.isArray(error.data?.detail)) {
    return error.data.detail.map((item) => item.msg).join('. ')
  }

  return fallback
}
