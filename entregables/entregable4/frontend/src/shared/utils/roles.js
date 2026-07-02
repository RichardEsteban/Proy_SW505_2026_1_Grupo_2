export const ROLES = {
  ADMIN: 'ADMIN',
  SUPERVISOR_ALMACEN: 'SUPERVISOR_ALMACEN',
  SUPERVISOR_SUCURSAL: 'SUPERVISOR_SUCURSAL',
  VENDEDOR: 'VENDEDOR'
}

export const ROLE_LABELS = {
  [ROLES.ADMIN]: 'Administrador General',
  [ROLES.SUPERVISOR_ALMACEN]: 'Supervisor de almacén',
  [ROLES.SUPERVISOR_SUCURSAL]: 'Supervisor de sucursal',
  [ROLES.VENDEDOR]: 'Vendedor'
}

export function canSeeAllLocations(role) {
  return [ROLES.ADMIN, ROLES.SUPERVISOR_ALMACEN].includes(role)
}
