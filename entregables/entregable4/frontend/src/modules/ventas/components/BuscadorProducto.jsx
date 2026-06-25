import { useState } from 'react';
import adminService from '@modules/admin/services/adminService.js';

export default function BuscadorProducto({ onAgregar }) {
  const [termino, setTermino] = useState('');
  const [resultados, setResultados] = useState([]);
  const [loading, setLoading] = useState(false);

  const buscar = async (t) => {
    setTermino(t);
    if (!t || t.length < 2) return setResultados([]);
    setLoading(true);
    try {
      const r = await adminService.listarProductos(t);
      setResultados(r || []);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative">
      <input
        className="input"
        placeholder="🔍 Buscar producto (nombre o SKU)..."
        value={termino}
        onChange={(e) => buscar(e.target.value)}
        autoFocus
      />
      {resultados.length > 0 && (
        <div className="absolute z-10 mt-1 w-full bg-white border rounded shadow-lg max-h-80 overflow-auto">
          {resultados.map((p) => (
            <button
              key={p.id}
              type="button"
              onClick={() => { onAgregar(p); setTermino(''); setResultados([]); }}
              className="w-full text-left p-3 hover:bg-primary-50 border-b last:border-0"
            >
              <div className="font-medium">{p.nombre}</div>
              <div className="text-xs text-gray-500">
                SKU: {p.sku} · S/ {p.precio_venta.toFixed(2)}
              </div>
            </button>
          ))}
        </div>
      )}
      {loading && <div className="absolute right-3 top-3 text-xs text-gray-400">Buscando...</div>}
    </div>
  );
}
