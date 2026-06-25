import api from '@shared/utils/api.js';

const reposicionService = {
  async listarSolicitudes(params = {}) {
    const { data } = await api.get('/reposicion/solicitudes', { params });
    return data;
  },

  async crearSolicitud(payload) {
    const { data } = await api.post('/reposicion/solicitudes', payload);
    return data;
  },

  async evaluar(solicitudId, accion, motivo = null) {
    const { data } = await api.post(`/reposicion/solicitudes/${solicitudId}/evaluar`, {
      accion, motivo,
    });
    return data;
  },

  async enviar(solicitudId) {
    const { data } = await api.post(`/reposicion/solicitudes/${solicitudId}/enviar`);
    return data;
  },

  async recibir(solicitudId) {
    const { data } = await api.post(`/reposicion/solicitudes/${solicitudId}/recibir`);
    return data;
  },
};

export default reposicionService;
