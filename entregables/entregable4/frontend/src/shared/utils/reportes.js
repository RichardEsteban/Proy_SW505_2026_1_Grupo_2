export const REPORTE_TABS = {
  RESUMEN: 'RESUMEN',
  VENTAS: 'VENTAS',
  PRODUCTOS: 'PRODUCTOS',
  STOCK: 'STOCK',
  KARDEX: 'KARDEX',
  COMPRAS: 'COMPRAS',
  REPOSICIONES: 'REPOSICIONES'
}

export const ESTADOS_COMPRA = ['SOLICITADO', 'EN_TRANSITO', 'RECIBIDO', 'CANCELADO']

export function numberValue(value) {
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : 0
}

export function formatDate(value) {
  if (!value) return '-'

  const date = new Date(`${value}T00:00:00`)
  if (Number.isNaN(date.getTime())) return value

  return new Intl.DateTimeFormat('es-PE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  }).format(date)
}

export function formatDateTime(value) {
  if (!value) return '-'

  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value

  return new Intl.DateTimeFormat('es-PE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

export function localDateTimeToIso(value) {
  if (!value) return undefined
  return value.length === 16 ? `${value}:00` : value
}

export function getApiErrorMessage(error, fallback = 'No se pudo completar la operación') {
  if (Array.isArray(error?.data?.detail)) {
    return error.data.detail.map((item) => item.msg).join(', ')
  }

  return error?.message || fallback
}

export function getEstadoTone(estado) {
  const tones = {
    RECIBIDO: 'green',
    RECIBIDA: 'green',
    ACEPTADO: 'green',
    SOLICITADO: 'amber',
    ENVIADO: 'amber',
    EN_REVISION: 'amber',
    EN_TRANSITO: 'amber',
    CANCELADO: 'red',
    CANCELADA: 'red',
    RECHAZADA: 'red',
    STOCK_AGOTADO: 'red',
    STOCK_MINIMO: 'amber',
    INGRESO: 'green',
    SALIDA: 'red'
  }

  return tones[estado] || 'slate'
}

export function getMaxValue(items, field) {
  return Math.max(1, ...items.map((item) => numberValue(item[field])))
}

export function buildResumenCards(resumen) {
  return [
    {
      title: 'Ventas totales',
      value: resumen.totalVentas,
      description: `${resumen.cantidadVentas || 0} venta(s) registradas`,
      money: true
    },
    {
      title: 'Ticket promedio',
      value: resumen.ticketPromedio,
      description: 'Promedio por venta',
      money: true
    },
    {
      title: 'Stock bajo',
      value: resumen.productosConStockBajo,
      description: 'Productos bajo mínimo'
    },
    {
      title: 'Alertas pendientes',
      value: resumen.alertasPendientes,
      description: 'Alertas sin leer'
    },
    {
      title: 'Compras abiertas',
      value: resumen.ordenesCompraAbiertas,
      description: 'Solicitado o en tránsito'
    },
    {
      title: 'Reposiciones abiertas',
      value: resumen.reposicionesAbiertas,
      description: 'Solicitudes en proceso'
    }
  ]
}
