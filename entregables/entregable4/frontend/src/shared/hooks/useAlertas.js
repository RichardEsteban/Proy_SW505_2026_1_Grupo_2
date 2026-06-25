import { useEffect, useState } from 'react';
import api from '@shared/utils/api.js';

/**
 * Hook que obtiene las alertas de stock activas.
 * Polling cada 60s. Ajustar según necesidad.
 */
export function useAlertas(sucursalId = null, intervalMs = 60000) {
  const [alertas, setAlertas] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!sucursalId) {
      setAlertas([]);
      return;
    }
    let cancelado = false;
    const cargar = async () => {
      setLoading(true);
      try {
        const r = await api.get('/inventario/verificar-stock-minimo', {
          params: { sucursal_id: sucursalId },
        });
        if (!cancelado) {
          setAlertas(r.data?.alertas || []);
          setError(null);
        }
      } catch (e) {
        if (!cancelado) setError(e);
      } finally {
        if (!cancelado) setLoading(false);
      }
    };
    cargar();
    const t = setInterval(cargar, intervalMs);
    return () => {
      cancelado = true;
      clearInterval(t);
    };
  }, [sucursalId, intervalMs]);

  return { alertas, loading, error };
}

export default useAlertas;
