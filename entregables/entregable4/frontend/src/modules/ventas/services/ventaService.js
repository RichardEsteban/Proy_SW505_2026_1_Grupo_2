import api from '@shared/utils/api.js';

const ventaService = {
  async listar(params = {}) {
    const { data } = await api.get('/ventas', { params });
    return data;
  },

  async calcular(items) {
    const { data } = await api.post('/ventas/calcular', { items });
    return data;
  },

  async registrar(payload) {
    const { data } = await api.post('/ventas', payload);
    return data;
  },

  async generarComprobante(ventaId) {
    const { data } = await api.post(`/ventas/${ventaId}/comprobante`);
    return data;
  },

  async anular(ventaId) {
    const { data } = await api.post(`/ventas/${ventaId}/anular`);
    return data;
  },
};

export default ventaService;
