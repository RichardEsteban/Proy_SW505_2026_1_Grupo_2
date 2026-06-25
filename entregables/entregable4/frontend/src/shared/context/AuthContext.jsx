import { createContext, useEffect, useState, useCallback } from 'react';
import authService from '@modules/auth/services/authService.js';

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const raw = localStorage.getItem('user');
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  });
  const [token, setToken] = useState(() => localStorage.getItem('access_token'));
  const [loading, setLoading] = useState(false);

  const persistir = useCallback((tokenValue, userValue) => {
    setToken(tokenValue);
    setUser(userValue);
    if (tokenValue) {
      localStorage.setItem('access_token', tokenValue);
      localStorage.setItem('user', JSON.stringify(userValue));
    } else {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
    }
  }, []);

  const login = useCallback(async (username, password) => {
    setLoading(true);
    try {
      const r = await authService.login(username, password);
      persistir(r.access_token, {
        id: r.usuario_id,
        username: r.username,
        nombre_completo: r.nombre_completo,
        rol: r.rol,
        sucursal_id: r.sucursal_id,
        debe_cambiar_password: r.debe_cambiar_password,
      });
      return r;
    } finally {
      setLoading(false);
    }
  }, [persistir]);

  const logout = useCallback(() => {
    persistir(null, null);
  }, [persistir]);

  const cambiarPassword = useCallback(async (actual, nueva) => {
    return authService.cambiarPassword(actual, nueva);
  }, []);

  useEffect(() => {
    // Si el token cambia desde otra pestaña
    const handler = (e) => {
      if (e.key === 'access_token') {
        setToken(e.newValue);
        try {
          setUser(e.newValue ? JSON.parse(localStorage.getItem('user') || 'null') : null);
        } catch {
          setUser(null);
        }
      }
    };
    window.addEventListener('storage', handler);
    return () => window.removeEventListener('storage', handler);
  }, []);

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout, cambiarPassword }}>
      {children}
    </AuthContext.Provider>
  );
}
