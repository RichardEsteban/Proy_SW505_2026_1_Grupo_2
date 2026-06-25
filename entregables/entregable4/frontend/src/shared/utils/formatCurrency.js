export const formatCurrency = (value, currency = 'PEN') => {
  const n = Number(value || 0);
  return new Intl.NumberFormat('es-PE', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
  }).format(n);
};

export const formatNumber = (value, decimals = 2) => {
  const n = Number(value || 0);
  return n.toFixed(decimals);
};

export const formatDate = (iso) => {
  if (!iso) return '-';
  const d = new Date(iso);
  return d.toLocaleDateString('es-PE', {
    year: 'numeric', month: '2-digit', day: '2-digit',
  });
};

export const formatDateTime = (iso) => {
  if (!iso) return '-';
  const d = new Date(iso);
  return d.toLocaleString('es-PE');
};
