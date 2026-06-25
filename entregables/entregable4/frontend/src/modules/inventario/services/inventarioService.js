import api from '@shared/utils/api.js';

const inventarioService = {
  async disponibilidad(sucursalId, termino = '', soloBajoMinimo = false) {
    const { data } = await api.get('/inventario/disponibilidad', {
      params: { sucursal_id: sucursalId, termino, solo_bajo_minimo: soloBajoMinimo },
    });
    return data;
  },

  async verificarStockMinimo(sucursalId) {
    const { data } = await api.post('/inventario/verificar-stock-minimo', null, {
      params: { sucursal_id: sucursalId },
    });
    return data;
  },
};

export default inventarioService;
