import { apiRequest } from '@/shared/api/client'

export function getResumen() {
  return apiRequest('/reportes/resumen')
}
