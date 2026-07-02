import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { clearToken, getStoredToken, saveToken } from '@/shared/api/client'
import { loginRequest, logoutRequest, meRequest } from '@/shared/api/authApi'

const USER_KEY = 'sistema_mype_usuario'
const INACTIVITY_MINUTES = Number(import.meta.env.VITE_SESSION_INACTIVITY_MINUTES || 30)
const INACTIVITY_LIMIT_MS = INACTIVITY_MINUTES * 60 * 1000
const SESSION_HEARTBEAT_MS = Number(import.meta.env.VITE_SESSION_HEARTBEAT_MS || 60000)

// El navegador controla la inactividad visible y el backend confirma que la sesión siga viva.
const AuthContext = createContext(null)

function getStoredUser() {
  const raw = localStorage.getItem(USER_KEY)

  if (!raw) return null

  try {
    return JSON.parse(raw)
  } catch {
    localStorage.removeItem(USER_KEY)
    return null
  }
}

function saveUser(usuario) {
  localStorage.setItem(USER_KEY, JSON.stringify(usuario))
}

function clearUser() {
  localStorage.removeItem(USER_KEY)
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => getStoredToken())
  const [usuario, setUsuario] = useState(() => getStoredUser())
  const [loading, setLoading] = useState(Boolean(getStoredToken()))

  const clearAuthState = useCallback(() => {
    clearToken()
    clearUser()
    setToken(null)
    setUsuario(null)
  }, [])

  const login = useCallback(async (credentials) => {
    const data = await loginRequest(credentials)

    saveToken(data.access_token)
    saveUser(data.usuario)
    setToken(data.access_token)
    setUsuario(data.usuario)

    return data.usuario
  }, [])

  const logout = useCallback(async () => {
    const currentToken = getStoredToken()

    try {
      if (currentToken) {
        await logoutRequest()
      }
    } catch {
      // Si el backend ya cerró la sesión o el token expiró, igual limpiamos el navegador.
    } finally {
      clearAuthState()
    }
  }, [clearAuthState])

  useEffect(() => {
    let isMounted = true

    async function verifySession() {
      if (!token) {
        setLoading(false)
        return
      }

      try {
        const currentUser = await meRequest()

        if (isMounted) {
          setUsuario(currentUser)
          saveUser(currentUser)
        }
      } catch {
        if (isMounted) clearAuthState()
      } finally {
        if (isMounted) setLoading(false)
      }
    }

    verifySession()

    return () => {
      isMounted = false
    }
  }, [clearAuthState, token])

  useEffect(() => {
    function handleExpiredSession() {
      clearAuthState()
    }

    window.addEventListener('auth:expired', handleExpiredSession)
    return () => window.removeEventListener('auth:expired', handleExpiredSession)
  }, [clearAuthState])

  useEffect(() => {
    if (!token) return undefined

    // Cierra sesión cuando el usuario deja de interactuar con la interfaz.
    let timeoutId

    function scheduleAutoLogout() {
      window.clearTimeout(timeoutId)
      timeoutId = window.setTimeout(() => {
        logout()
      }, INACTIVITY_LIMIT_MS)
    }

    const activityEvents = ['click', 'mousemove', 'keydown', 'scroll', 'touchstart']
    activityEvents.forEach((eventName) => {
      window.addEventListener(eventName, scheduleAutoLogout, { passive: true })
    })

    scheduleAutoLogout()

    return () => {
      window.clearTimeout(timeoutId)
      activityEvents.forEach((eventName) => window.removeEventListener(eventName, scheduleAutoLogout))
    }
  }, [logout, token])

  useEffect(() => {
    if (!token) return undefined

    // Latido periódico: evita sesiones colgadas y permite liberar cuentas bloqueadas.
    let cancelled = false

    async function keepSessionAlive() {
      try {
        await meRequest()
      } catch {
        if (!cancelled) clearAuthState()
      }
    }

    const intervalId = window.setInterval(keepSessionAlive, SESSION_HEARTBEAT_MS)

    return () => {
      cancelled = true
      window.clearInterval(intervalId)
    }
  }, [clearAuthState, token])

  const value = useMemo(() => ({
    token,
    usuario,
    loading,
    isAuthenticated: Boolean(token && usuario),
    login,
    logout
  }), [token, usuario, loading, login, logout])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)

  if (!context) {
    throw new Error('useAuth debe usarse dentro de AuthProvider')
  }

  return context
}
