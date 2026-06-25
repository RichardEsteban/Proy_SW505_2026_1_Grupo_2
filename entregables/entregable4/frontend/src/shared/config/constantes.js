/**
 * Constantes globales de la aplicación.
 *
 * En desarrollo local con Docker:  http://localhost:8000/api
 * En producción: cambiar a la URL del backend desplegado.
 */
export const API_URL =
  import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const APP_NAME = 'Sistema Inventario';
export const APP_ENV = 'production';
export const APP_VERSION = '1.0.0';

export const MONEDA = 'PEN';
export const IGV_PORCENTAJE = 18;

export const STORAGE_KEYS = {
  TOKEN: 'access_token',
  USER: 'user',
};