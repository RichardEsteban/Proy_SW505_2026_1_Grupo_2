export function formatMoney(value) {
  const numericValue = Number(value ?? 0)

  return new Intl.NumberFormat('es-PE', {
    style: 'currency',
    currency: 'PEN',
    minimumFractionDigits: 2
  }).format(numericValue)
}
