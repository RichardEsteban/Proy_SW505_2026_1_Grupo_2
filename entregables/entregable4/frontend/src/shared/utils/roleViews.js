import { ROLES } from '@/shared/utils/roles'

export const ROLE_VIEW_LABELS = {
  [ROLES.ADMIN]: 'Administrador General',
  [ROLES.SUPERVISOR_ALMACEN]: 'Supervisor de Almacén Central',
  [ROLES.SUPERVISOR_SUCURSAL]: 'Supervisor de Sucursal',
  [ROLES.VENDEDOR]: 'Vendedor'
}

export const ROLE_DASHBOARD_DESCRIPTIONS = {
  [ROLES.ADMIN]: 'Panel administrativo para gestionar usuarios, roles, productos, categorías, proveedores, órdenes de compra, ubicaciones, dashboard y reportes globales.',
  [ROLES.SUPERVISOR_ALMACEN]: 'Vista operativa del almacén central: inventario, sucursales abastecidas, recepciones, solicitudes de reposición, despachos y movimientos.',
  [ROLES.SUPERVISOR_SUCURSAL]: 'Vista de la sucursal asignada: inventario local, solicitudes de reposición, recepciones, alertas de stock y movimientos.',
  [ROLES.VENDEDOR]: 'Vista simple para consultar inventario disponible y registrar nuevas ventas en la sucursal asignada.'
}

export const menuByRole = {
  [ROLES.ADMIN]: [
    { label: 'Dashboard', path: '/dashboard' },
    { label: 'Usuarios y roles', path: '/usuarios' },
    { label: 'Productos', path: '/productos' },
    { label: 'Categorías', path: '/categorias' },
    { label: 'Proveedores', path: '/proveedores' },
    { label: 'Orden de compra', path: '/ordenes-compra' },
    { label: 'Ubicaciones', path: '/ubicaciones' },
    { label: 'Reportes', path: '/reportes' }
  ],
  [ROLES.SUPERVISOR_ALMACEN]: [
    { label: 'Dashboard', path: '/dashboard' },
    { label: 'Inventario', path: '/inventario' },
    { label: 'Sucursales', path: '/sucursales' },
    { label: 'Recepciones', path: '/recepciones' },
    { label: 'Solicitudes de reposición', path: '/solicitudes-reposicion' },
    { label: 'Despachos', path: '/despachos' },
    { label: 'Movimientos', path: '/movimientos' }
  ],
  [ROLES.SUPERVISOR_SUCURSAL]: [
    { label: 'Dashboard', path: '/dashboard' },
    { label: 'Inventario', path: '/inventario' },
    { label: 'Solicitudes de reposición', path: '/solicitudes-reposicion' },
    { label: 'Recepciones', path: '/recepciones' },
    { label: 'Alertas de stock', path: '/alertas-stock' },
    { label: 'Movimientos', path: '/movimientos' }
  ],
  [ROLES.VENDEDOR]: [
    { label: 'Inventario', path: '/inventario' },
    { label: 'Nueva venta', path: '/ventas' }
  ]
}

export const routeRoles = {
  '/dashboard': [ROLES.ADMIN, ROLES.SUPERVISOR_ALMACEN, ROLES.SUPERVISOR_SUCURSAL],
  '/usuarios': [ROLES.ADMIN],
  '/productos': [ROLES.ADMIN],
  '/categorias': [ROLES.ADMIN],
  '/proveedores': [ROLES.ADMIN],
  '/ordenes-compra': [ROLES.ADMIN],
  '/ubicaciones': [ROLES.ADMIN],
  '/inventario': [ROLES.SUPERVISOR_ALMACEN, ROLES.SUPERVISOR_SUCURSAL, ROLES.VENDEDOR],
  '/sucursales': [ROLES.SUPERVISOR_ALMACEN],
  '/solicitudes-reposicion': [ROLES.SUPERVISOR_ALMACEN, ROLES.SUPERVISOR_SUCURSAL],
  '/despachos': [ROLES.SUPERVISOR_ALMACEN],
  '/ventas': [ROLES.VENDEDOR],
  '/movimientos': [ROLES.SUPERVISOR_ALMACEN, ROLES.SUPERVISOR_SUCURSAL],
  '/reportes': [ROLES.ADMIN],
  '/alertas-stock': [ROLES.SUPERVISOR_SUCURSAL],
  '/recepciones': [ROLES.SUPERVISOR_ALMACEN, ROLES.SUPERVISOR_SUCURSAL]
}

export function getMenuForRole(role) {
  return menuByRole[role] || [{ label: 'Dashboard', path: '/dashboard' }]
}

export function getDefaultPathForRole(role) {
  if (role === ROLES.VENDEDOR) return '/inventario'
  return '/dashboard'
}

export function isRouteAllowed(path, role) {
  const allowed = routeRoles[path]
  return !allowed || allowed.includes(role)
}

export function isCentralWarehouse(item = {}) {
  const tipo = String(item.tipoUbicacion || item.tipo || '').toUpperCase()
  const nombre = String(item.nombreUbicacion || item.ubicacion || '').toLowerCase()
  return tipo === 'ALMACEN' || nombre.includes('central') || nombre.includes('almacén') || nombre.includes('almacen')
}

export function isBranch(item = {}) {
  const tipo = String(item.tipoUbicacion || item.tipo || '').toUpperCase()
  return tipo === 'SUCURSAL' || !isCentralWarehouse(item)
}

export function getStockState(item = {}) {
  const estado = item.estadoStock
  if (estado) return estado
  const stock = Number(item.stockDisponible || 0)
  const minimo = Number(item.stockMinimo || 0)
  if (stock <= 0) return 'STOCK_AGOTADO'
  if (minimo > 0 && stock <= minimo) return 'STOCK_MINIMO'
  return 'NORMAL'
}

export function stockTone(item = {}) {
  const state = getStockState(item)
  if (state === 'STOCK_AGOTADO') return 'red'
  if (state === 'STOCK_MINIMO') return 'amber'
  return 'green'
}

export function stockLabel(item = {}) {
  const state = getStockState(item)
  if (state === 'STOCK_AGOTADO') return 'Agotado'
  if (state === 'STOCK_MINIMO') return 'Bajo stock'
  return 'Disponible'
}

export function sumStock(items = []) {
  return items.reduce((total, item) => total + Number(item.stockDisponible || 0), 0)
}

export function countLowStock(items = []) {
  return items.filter((item) => getStockState(item) === 'STOCK_MINIMO').length
}

export function countCriticalStock(items = []) {
  return items.filter((item) => getStockState(item) === 'STOCK_AGOTADO').length
}

export function formatDateTime(value) {
  if (!value) return '-'
  return new Intl.DateTimeFormat('es-PE', {
    dateStyle: 'short',
    timeStyle: 'short'
  }).format(new Date(value))
}
