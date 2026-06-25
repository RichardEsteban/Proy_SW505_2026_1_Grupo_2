import api from '@shared/utils/api.js';

const sucursalService = {
  async dashboard(sucursalId) {
    const { data } = await api.get('/reportes/dashboard', {
      params: sucursalId ? { sucursal_id: sucursalId } : {},
    });
    return data;
  },

  async reporteVentas(desde, hasta, sucursalId) {
    const { data } = await api.get('/reportes/ventas', {
      params: { fecha_desde: desde, fecha_hasta: hasta, sucursal_id: sucursalId },
    });
    return data;
  },
};

export default sucursalService;
