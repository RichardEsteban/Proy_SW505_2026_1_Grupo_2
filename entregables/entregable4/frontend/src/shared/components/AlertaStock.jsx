import { useState } from 'react';
import { useAlertas } from '@shared/hooks/useAlertas.js';
import { formatDateTime } from '@shared/utils/formatCurrency.js';

export default function AlertaStock({ sucursalId }) {
  const { alertas } = useAlertas(sucursalId);
  const [abierto, setAbierto] = useState(false);

  const count = alertas.length;
  if (!count) return null;

  return (
    <div className="relative">
      <button
        onClick={() => setAbierto((v) => !v)}
        className="relative p-2 rounded-full bg-red-100 text-red-700 hover:bg-red-200"
        aria-label="Alertas"
      >
        🔔
        <span className="absolute -top-1 -right-1 bg-red-600 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
          {count}
        </span>
      </button>
      {abierto && (
        <div className="absolute right-0 mt-2 w-80 bg-white shadow-lg rounded-lg border border-gray-200 z-50">
          <div className="p-3 border-b font-semibold text-sm">Alertas de stock</div>
          <ul className="max-h-80 overflow-auto divide-y">
            {alertas.map((a) => (
              <li key={a.id} className="p-3 text-sm">
                <div className="font-medium">{a.mensaje}</div>
                <div className="text-xs text-gray-500">
                  {a.tipo} · {formatDateTime(a.created_at)}
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
