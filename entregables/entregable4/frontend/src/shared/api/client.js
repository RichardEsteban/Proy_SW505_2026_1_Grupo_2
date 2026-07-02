// En red local, otras laptops abren el frontend con el IP del host.
// Por eso la API se construye con el mismo host y solo cambia al puerto 8000.
const DEFAULT_API_URL = `${window.location.protocol}//${window.location.hostname}:8000/api`
const API_URL = import.meta.env.VITE_API_URL || DEFAULT_API_URL
const TOKEN_KEY = 'sistema_mype_token'

export function getStoredToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function saveToken(token) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY)
}

async function parseResponse(response) {
  const contentType = response.headers.get('content-type') || ''

  if (contentType.includes('application/json')) {
    return response.json()
  }

  return response.text()
}

export async function apiRequest(path, options = {}) {
  const token = getStoredToken()
  const hasBody = options.body !== undefined && options.body !== null
  const isFormData = hasBody && options.body instanceof FormData

  const headers = {
    ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
    body: hasBody && !isFormData ? JSON.stringify(options.body) : options.body
  })

  const data = await parseResponse(response)

  if (!response.ok) {
    if (response.status === 401 && token) {
      window.dispatchEvent(new CustomEvent('auth:expired'))
    }

    const message = typeof data === 'object' && data?.detail
      ? data.detail
      : 'Ocurrió un error al comunicarse con el servidor'

    const error = new Error(message)
    error.status = response.status
    error.data = data
    throw error
  }

  return data
}

export { API_URL }
