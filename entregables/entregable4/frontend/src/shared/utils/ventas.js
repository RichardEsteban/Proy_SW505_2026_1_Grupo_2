import { ROLES } from '@/shared/utils/roles'

export function canCreateSale(role) {
  return [ROLES.ADMIN, ROLES.VENDEDOR, ROLES.SUPERVISOR_SUCURSAL].includes(role)
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

export function formatDateTime(value) {
  if (!value) return '-'

  return new Intl.DateTimeFormat('es-PE', {
    dateStyle: 'short',
    timeStyle: 'short'
  }).format(new Date(value))
}

export function toDateTimeLocalValue(date = new Date()) {
  const pad = (value) => String(value).padStart(2, '0')
  const year = date.getFullYear()
  const month = pad(date.getMonth() + 1)
  const day = pad(date.getDate())
  const hours = pad(date.getHours())
  const minutes = pad(date.getMinutes())
  return `${year}-${month}-${day}T${hours}:${minutes}`
}

export function localDateTimeToIso(value) {
  if (!value) return undefined
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? undefined : date.toISOString()
}

export function moneyNumber(value) {
  const number = Number(value ?? 0)
  return Number.isNaN(number) ? 0 : number
}

export function calculateLine({ precioVenta = 0, porcentajeIgv = 0, cantidad = 0 }) {
  const qty = moneyNumber(cantidad)
  const price = moneyNumber(precioVenta)
  const igvPercent = moneyNumber(porcentajeIgv)
  const totalLinea = roundMoney(price * qty)

  if (igvPercent <= 0) {
    return {
      subtotal: totalLinea,
      igv: 0,
      total: totalLinea
    }
  }

  const divisor = 1 + (igvPercent / 100)
  const subtotal = roundMoney(totalLinea / divisor)
  const igv = roundMoney(totalLinea - subtotal)

  return {
    subtotal,
    igv,
    total: totalLinea
  }
}

export function roundMoney(value) {
  return Math.round((moneyNumber(value) + Number.EPSILON) * 100) / 100
}

export function getClienteLabel(cliente) {
  if (!cliente) return 'Cliente no especificado'
  return cliente.nombreMostrar || cliente.razonSocial || `${cliente.nombres || ''} ${cliente.apellidos || ''}`.trim() || `Cliente #${cliente.idCliente}`
}

export function buildStockMap(inventario = []) {
  const map = new Map()
  inventario.forEach((item) => {
    map.set(Number(item.idProducto), Number(item.stockDisponible || 0))
  })
  return map
}
