import { apiRequest } from '@/shared/api/client'

export function loginRequest({ correoElectronico, contrasena, forzarCierreSesion = false }) {
  return apiRequest('/auth/login', {
    method: 'POST',
    body: { correoElectronico, contrasena, forzarCierreSesion }
  })
}

export function meRequest() {
  return apiRequest('/auth/me')
}

export function forgotPasswordRequest({ correoElectronico }) {
  return apiRequest('/auth/forgot-password', {
    method: 'POST',
    body: { correoElectronico }
  })
}

export function verifyResetCodeRequest({ correoElectronico, codigo }) {
  return apiRequest('/auth/verify-reset-code', {
    method: 'POST',
    body: { correoElectronico, codigo }
  })
}

export function resetPasswordRequest({ correoElectronico, codigo, nuevaContrasena, confirmarContrasena }) {
  return apiRequest('/auth/reset-password', {
    method: 'POST',
    body: { correoElectronico, codigo, nuevaContrasena, confirmarContrasena }
  })
}


export function logoutRequest() {
  return apiRequest('/auth/logout', {
    method: 'POST'
  })
}
