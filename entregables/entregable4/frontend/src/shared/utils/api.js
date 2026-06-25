import axios from 'axios';
import toast from 'react-hot-toast';
import { API_URL, STORAGE_KEYS } from '@shared/config/constantes.js';

const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

// Interceptor: agrega el token JWT a cada request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem(STORAGE_KEYS.TOKEN);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor: maneja 401 y errores globales
api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem(STORAGE_KEYS.TOKEN);
      localStorage.removeItem(STORAGE_KEYS.USER);
      if (!window.location.pathname.startsWith('/login')) {
        window.location.href = '/login';
      }
    } else if (err.response?.status >= 500) {
      toast.error('Error del servidor. Intenta nuevamente.');
    }
    return Promise.reject(err);
  }
);

export default api;
export { API_URL };