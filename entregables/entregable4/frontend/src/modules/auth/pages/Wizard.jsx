import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import authService from '@modules/auth/services/authService.js';

const PASOS = ['Empresa', 'Administrador', 'Sucursal & Almacén', 'Confirmar'];

export default function Wizard() {
  const navigate = useNavigate();
  const [paso, setPaso] = useState(0);
  const [loading, setLoading] = useState(false);
  const [datos, setDatos] = useState({
    empresa_nombre: '',
    empresa_ruc: '',
    admin_dni: '',
    admin_nombre: '',
    admin_apellido: '',
    admin_email: '',
    admin_username: '',
    admin_password: '',
    igv_porcentaje: 18,
    moneda: 'PEN',
    sucursal_nombre: 'Sucursal Principal',
    almacen_nombre: 'Almacén Central',
  });
  const set = (k, v) => setDatos((d) => ({ ...d, [k]: v }));

  const submit = async () => {
    setLoading(true);
    try {
      await authService.wizardInicial(datos);
      toast.success('Sistema inicializado. Inicia sesión.');
      navigate('/login');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Error en wizard');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <div className="card w-full max-w-2xl">
        <h1 className="text-2xl font-bold mb-1">Asistente de configuración inicial</h1>
        <p className="text-sm text-gray-500 mb-6">Paso {paso + 1} de {PASOS.length}: {PASOS[paso]}</p>
        <div className="w-full bg-gray-200 rounded-full h-2 mb-6">
          <div className="bg-primary-600 h-2 rounded-full transition-all" style={{ width: `${((paso + 1) / PASOS.length) * 100}%` }} />
        </div>

        {paso === 0 && (
          <div className="space-y-3">
            <div><label className="label">Nombre de la empresa</label><input className="input" value={datos.empresa_nombre} onChange={(e) => set('empresa_nombre', e.target.value)} required /></div>
            <div><label className="label">RUC</label><input className="input" value={datos.empresa_ruc} onChange={(e) => set('empresa_ruc', e.target.value)} required /></div>
            <div className="grid grid-cols-2 gap-3">
              <div><label className="label">IGV %</label><input className="input" type="number" step="0.01" value={datos.igv_porcentaje} onChange={(e) => set('igv_porcentaje', parseFloat(e.target.value))} /></div>
              <div><label className="label">Moneda</label><input className="input" value={datos.moneda} onChange={(e) => set('moneda', e.target.value)} /></div>
            </div>
          </div>
        )}

        {paso === 1 && (
          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div><label className="label">DNI</label><input className="input" value={datos.admin_dni} onChange={(e) => set('admin_dni', e.target.value)} required /></div>
              <div><label className="label">Username</label><input className="input" value={datos.admin_username} onChange={(e) => set('admin_username', e.target.value)} required /></div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div><label className="label">Nombre</label><input className="input" value={datos.admin_nombre} onChange={(e) => set('admin_nombre', e.target.value)} required /></div>
              <div><label className="label">Apellido</label><input className="input" value={datos.admin_apellido} onChange={(e) => set('admin_apellido', e.target.value)} required /></div>
            </div>
            <div><label className="label">Email</label><input className="input" type="email" value={datos.admin_email} onChange={(e) => set('admin_email', e.target.value)} required /></div>
            <div><label className="label">Password (mín 8)</label><input className="input" type="password" value={datos.admin_password} onChange={(e) => set('admin_password', e.target.value)} required minLength={8} /></div>
          </div>
        )}

        {paso === 2 && (
          <div className="space-y-3">
            <div><label className="label">Nombre de la sucursal</label><input className="input" value={datos.sucursal_nombre} onChange={(e) => set('sucursal_nombre', e.target.value)} /></div>
            <div><label className="label">Nombre del almacén</label><input className="input" value={datos.almacen_nombre} onChange={(e) => set('almacen_nombre', e.target.value)} /></div>
          </div>
        )}

        {paso === 3 && (
          <div className="space-y-2 text-sm bg-gray-50 p-4 rounded">
            <div><b>Empresa:</b> {datos.empresa_nombre} (RUC {datos.empresa_ruc})</div>
            <div><b>Admin:</b> {datos.admin_nombre} {datos.admin_apellido} ({datos.admin_username})</div>
            <div><b>Sucursal:</b> {datos.sucursal_nombre}</div>
            <div><b>Almacén:</b> {datos.almacen_nombre}</div>
            <div><b>IGV:</b> {datos.igv_porcentaje}% {datos.moneda}</div>
          </div>
        )}

        <div className="flex justify-between mt-6">
          <button className="btn-secondary" disabled={paso === 0} onClick={() => setPaso(paso - 1)}>← Atrás</button>
          {paso < PASOS.length - 1 ? (
            <button className="btn-primary" onClick={() => setPaso(paso + 1)}>Siguiente →</button>
          ) : (
            <button className="btn-primary" onClick={submit} disabled={loading}>{loading ? 'Inicializando...' : 'Inicializar'}</button>
          )}
        </div>
      </div>
    </div>
  );
}
