import { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useAuth } from '@shared/hooks/useAuth.js';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(username, password);
      toast.success('Bienvenido');
      const next = location.state?.from?.pathname || '/';
      navigate(next, { replace: true });
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Error al iniciar sesión');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100 p-4">
      <div className="card w-full max-w-md">
        <h1 className="text-2xl font-bold text-center mb-1">Sistema Inventario</h1>
        <p className="text-center text-sm text-gray-500 mb-6">Inicia sesión para continuar</p>
        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <label className="label">Usuario</label>
            <input className="input" value={username} onChange={(e) => setUsername(e.target.value)} required autoFocus />
          </div>
          <div>
            <label className="label">Contraseña</label>
            <input className="input" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </div>
          <button className="btn-primary w-full" disabled={loading}>
            {loading ? 'Ingresando...' : 'Ingresar'}
          </button>
        </form>
        <div className="mt-4 flex justify-between text-sm">
          <Link to="/recuperar-password" className="text-primary-600 hover:underline">¿Olvidaste tu contraseña?</Link>
          <Link to="/wizard" className="text-primary-600 hover:underline">Configuración inicial</Link>
        </div>
      </div>
    </div>
  );
}
