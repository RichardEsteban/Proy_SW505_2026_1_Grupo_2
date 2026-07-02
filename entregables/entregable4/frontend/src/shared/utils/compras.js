export const ESTADOS_COMPRA = {
  SOLICITADO: 'SOLICITADO',
  EN_TRANSITO: 'EN_TRANSITO',
  RECIBIDO: 'RECIBIDO',
  CANCELADO: 'CANCELADO'
}

export const ESTADO_COMPRA_LABELS = {
  [ESTADOS_COMPRA.SOLICITADO]: 'Pendiente recepción',
  [ESTADOS_COMPRA.EN_TRANSITO]: 'En tránsito',
  [ESTADOS_COMPRA.RECIBIDO]: 'Recibida',
  [ESTADOS_COMPRA.CANCELADO]: 'Cancelada'
}

export function getEstadoCompraTone(estado) {
  const tones = {
    [ESTADOS_COMPRA.SOLICITADO]: 'amber',
    [ESTADOS_COMPRA.EN_TRANSITO]: 'slate',
    [ESTADOS_COMPRA.RECIBIDO]: 'green',
    [ESTADOS_COMPRA.CANCELADO]: 'red'
  }

  return tones[estado] || 'slate'
}

export function formatEstadoCompra(estado) {
  return ESTADO_COMPRA_LABELS[estado] || estado || '-'
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

export function moneyNumber(value) {
  const number = Number(value ?? 0)
  return Number.isFinite(number) ? number : 0
}

export function roundMoney(value) {
  return Math.round((moneyNumber(value) + Number.EPSILON) * 100) / 100
}

export function calculatePurchaseLine({ precioCompraUnitario, cantidad, porcentajeIgv }) {
  const quantity = Number(cantidad || 0)
  const price = moneyNumber(precioCompraUnitario)
  const total = roundMoney(price * quantity)
  const igvRate = moneyNumber(porcentajeIgv)

  if (igvRate <= 0) {
    return { subtotal: total, igv: 0, total }
  }

  const divisor = 1 + igvRate / 100
  const subtotal = roundMoney(total / divisor)
  const igv = roundMoney(total - subtotal)

  return { subtotal, igv, total }
}

export function getApiErrorMessage(error, fallback) {
  if (typeof error?.message === 'string' && error.message.trim()) {
    return error.message
  }

  return fallback
}
