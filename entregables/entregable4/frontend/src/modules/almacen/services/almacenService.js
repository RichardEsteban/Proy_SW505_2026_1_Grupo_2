import api from '@shared/utils/api.js';

const almacenService = {
  async registrarEntrada(payload) {
    const { data } = await api.post('/almacen/entradas', payload);
    return data;
  },

  async registrarCompra(payload) {
    const { data } = await api.post('/almacen/compras', payload);
    return data;
  },

  async listarAlmacenes() {
    const { data } = await api.get('/admin/almacenes');
    return data;
  },

  async listarSucursales() {
    const { data } = await api.get('/admin/sucursales');
    return data;
  },
};

export default almacenService;
