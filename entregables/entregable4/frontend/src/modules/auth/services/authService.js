import api from '@shared/utils/api.js';

const authService = {
  async login(username, password) {
    const { data } = await api.post('/auth/login', { username, password });
    return data;
  },

  async cambiarPassword(passwordActual, passwordNueva) {
    const { data } = await api.post('/auth/cambiar-password', {
      password_actual: passwordActual,
      password_nueva: passwordNueva,
    });
    return data;
  },

  async recuperarPassword(email) {
    const { data } = await api.post('/auth/recuperar-password', { email });
    return data;
  },

  async restablecerPassword(token, passwordNueva) {
    const { data } = await api.post('/auth/restablecer-password', {
      token,
      password_nueva: passwordNueva,
    });
    return data;
  },

  async wizardInicial(payload) {
    const { data } = await api.post('/auth/wizard-inicial', payload);
    return data;
  },

  async me() {
    const { data } = await api.get('/auth/me');
    return data;
  },
};

export default authService;
