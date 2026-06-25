import api from '@shared/utils/api.js';

const adminService = {
  // Usuarios
  listarUsuarios: (sucursalId) => api.get('/admin/usuarios', { params: { sucursal_id: sucursalId } }).then((r) => r.data),
  crearUsuario: (payload) => api.post('/admin/usuarios', payload).then((r) => r.data),
  resetPassword: (id, password) => api.post(`/admin/usuarios/${id}/reset-password`, { password_temporal: password }).then((r) => r.data),

  // Productos
  listarProductos: (termino = '') => api.get('/admin/productos', { params: { termino } }).then((r) => r.data),
  crearProducto: (payload) => api.post('/admin/productos', payload).then((r) => r.data),

  // Sucursales / Almacenes
  listarSucursales: () => api.get('/admin/sucursales').then((r) => r.data),
  crearSucursal: (payload) => api.post('/admin/sucursales', payload).then((r) => r.data),
  listarAlmacenes: () => api.get('/admin/almacenes').then((r) => r.data),
  crearAlmacen: (payload) => api.post('/admin/almacenes', payload).then((r) => r.data),

  // Clientes
  listarClientes: (termino = '') => api.get('/admin/clientes', { params: { termino } }).then((r) => r.data),
  crearCliente: (payload) => api.post('/admin/clientes', payload).then((r) => r.data),

  // Proveedores
  listarProveedores: () => api.get('/admin/proveedores').then((r) => r.data),
  crearProveedor: (payload) => api.post('/admin/proveedores', payload).then((r) => r.data),
};

export default adminService;
