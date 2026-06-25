import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useAuth } from '@shared/hooks/useAuth.js';

export default function CambiarPassword() {
  const { cambiarPassword, user, logout } = useAuth();
  const navigate = useNavigate();
  const [actual, setActual] = useState('');
  const [nueva, setNueva] = useState('');
  const [confirmar, setConfirmar] = useState('');
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e) => {
    e.preventDefault();
    if (nueva !== confirmar) return toast.error('Las contraseñas no coinciden');
    if (nueva.length < 8) return toast.error('Mínimo 8 caracteres');
    setLoading(true);
    try {
      await cambiarPassword(actual, nueva);
      toast.success('Contraseña actualizada');
      logout();
      navigate('/login');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'No se pudo cambiar');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <div className="card w-full max-w-md">
        <h1 className="text-xl font-bold mb-1">Cambiar contraseña</h1>
        <p className="text-sm text-gray-500 mb-4">Hola {user?.nombre_completo}, actualiza tu contraseña.</p>
        <form onSubmit={onSubmit} className="space-y-3">
          <div>
            <label className="label">Actual</label>
            <input className="input" type="password" value={actual} onChange={(e) => setActual(e.target.value)} required />
          </div>
          <div>
            <label className="label">Nueva</label>
            <input className="input" type="password" value={nueva} onChange={(e) => setNueva(e.target.value)} required minLength={8} />
          </div>
          <div>
            <label className="label">Confirmar nueva</label>
            <input className="input" type="password" value={confirmar} onChange={(e) => setConfirmar(e.target.value)} required minLength={8} />
          </div>
          <button className="btn-primary w-full" disabled={loading}>{loading ? 'Guardando...' : 'Guardar'}</button>
        </form>
      </div>
    </div>
  );
}
