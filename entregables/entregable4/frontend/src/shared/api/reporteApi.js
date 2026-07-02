import { apiRequest } from '@/shared/api/client'

function buildQuery(params = {}) {
  const query = new URLSearchParams()

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      query.set(key, String(value))
    }
  })

  const queryString = query.toString()
  return queryString ? `?${queryString}` : ''
}

export function obtenerResumenReporte({ idUbicacion, desde, hasta } = {}) {
  return apiRequest(`/reportes/resumen${buildQuery({
    id_ubicacion: idUbicacion,
    desde,
    hasta
  })}`)
}

export function listarVentasPorFecha({ idUbicacion, desde, hasta } = {}) {
  return apiRequest(`/reportes/ventas-por-fecha${buildQuery({
    id_ubicacion: idUbicacion,
    desde,
    hasta
  })}`)
}

export function listarProductosMasVendidos({ idUbicacion, desde, hasta, limite = 10 } = {}) {
  return apiRequest(`/reportes/productos-mas-vendidos${buildQuery({
    id_ubicacion: idUbicacion,
    desde,
    hasta,
    limite
  })}`)
}

export function listarStockBajoReporte({ idUbicacion } = {}) {
  return apiRequest(`/reportes/stock-bajo${buildQuery({
    id_ubicacion: idUbicacion
  })}`)
}

export function listarKardexReporte({ idUbicacion, idProducto, desde, hasta, limite = 200 } = {}) {
  return apiRequest(`/reportes/kardex${buildQuery({
    id_ubicacion: idUbicacion,
    id_producto: idProducto,
    desde,
    hasta,
    limite
  })}`)
}

export function listarComprasReporte({ idUbicacion, estado, desde, hasta, limite = 100 } = {}) {
  return apiRequest(`/reportes/compras${buildQuery({
    id_ubicacion: idUbicacion,
    estado,
    desde,
    hasta,
    limite
  })}`)
}

export function listarReposicionesPorEstado({ idUbicacionDestino } = {}) {
  return apiRequest(`/reportes/reposiciones-por-estado${buildQuery({
    id_ubicacion_destino: idUbicacionDestino
  })}`)
}
