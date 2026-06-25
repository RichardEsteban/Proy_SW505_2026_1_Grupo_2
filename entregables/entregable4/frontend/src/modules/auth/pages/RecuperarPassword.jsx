import { useState } from 'react';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import authService from '@modules/auth/services/authService.js';

export default function RecuperarPassword() {
  const [email, setEmail] = useState('');
  const [enviado, setEnviado] = useState(false);
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await authService.recuperarPassword(email);
      setEnviado(true);
      toast.success('Si el email existe, recibirás instrucciones');
    } catch {
      toast.error('Error al procesar la solicitud');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <div className="card w-full max-w-md">
        <h1 className="text-xl font-bold mb-4">Recuperar contraseña</h1>
        {enviado ? (
          <div className="text-sm">
            Te enviamos un enlace de recuperación. Revisa tu bandeja.
            <div className="mt-4">
              <Link to="/login" className="btn-secondary">Volver al login</Link>
            </div>
          </div>
        ) : (
          <form onSubmit={onSubmit} className="space-y-3">
            <div>
              <label className="label">Email</label>
              <input className="input" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
            </div>
            <button className="btn-primary w-full" disabled={loading}>{loading ? 'Enviando...' : 'Enviar'}</button>
            <Link to="/login" className="block text-center text-sm text-primary-600 hover:underline">Volver al login</Link>
          </form>
        )}
      </div>
    </div>
  );
}
