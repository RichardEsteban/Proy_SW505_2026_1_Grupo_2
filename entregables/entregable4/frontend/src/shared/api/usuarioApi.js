import { apiRequest } from '@/shared/api/client'

export function listarUsuarios({ incluirInactivos = true } = {}) {
  const params = new URLSearchParams({ incluir_inactivos: String(incluirInactivos) })
  return apiRequest(`/usuarios?${params.toString()}`)
}

export function obtenerUsuario(idUsuario) {
  return apiRequest(`/usuarios/${idUsuario}`)
}

export function crearUsuario(payload) {
  return apiRequest('/usuarios', {
    method: 'POST',
    body: payload
  })
}

export function actualizarUsuario(idUsuario, payload) {
  return apiRequest(`/usuarios/${idUsuario}`, {
    method: 'PATCH',
    body: payload
  })
}

export function listarRoles() {
  return apiRequest('/usuarios/roles')
}

export function cambiarMiContrasena(payload) {
  return apiRequest('/usuarios/me/contrasena', {
    method: 'PUT',
    body: payload
  })
}
