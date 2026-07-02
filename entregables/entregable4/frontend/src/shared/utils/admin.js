import { ROLES, ROLE_LABELS } from '@/shared/utils/roles'

export function canManageAdmin(role) {
  return role === ROLES.ADMIN
}

export function roleLabel(role) {
  return ROLE_LABELS[role] || role || 'Sin rol'
}

export function locationTypeLabel(type) {
  const labels = {
    ALMACEN: 'Almacén',
    SUCURSAL: 'Sucursal'
  }

  return labels[type] || type || 'Sin tipo'
}

export function booleanStatus(value) {
  return value ? 'Activo' : 'Inactivo'
}

export function booleanTone(value) {
  return value ? 'green' : 'red'
}

export function formatTemporaryPassword(value) {
  return value ? 'Temporal' : 'Definitiva'
}

export function getApiErrorMessage(error, fallback = 'No se pudo completar la operación') {
  if (!error) return fallback

  if (typeof error.message === 'string' && error.message) return error.message

  if (Array.isArray(error.data?.detail)) {
    return error.data.detail.map((item) => item.msg).join('. ')
  }

  return fallback
}

export function normalizeNumber(value) {
  if (value === null || value === undefined || value === '') return ''
  const number = Number(value)
  return Number.isNaN(number) ? '' : String(number)
}
