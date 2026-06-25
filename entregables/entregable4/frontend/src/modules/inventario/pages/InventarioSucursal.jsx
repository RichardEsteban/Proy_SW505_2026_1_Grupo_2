import { useEffect, useState } from 'react';
import inventarioService from '@modules/inventario/services/inventarioService.js';
import Tabla from '@shared/components/Tabla.jsx';
import { useAuth } from '@shared/hooks/useAuth.js';
import { formatNumber } from '@shared/utils/formatCurrency.js';

export default function InventarioSucursal() {
  const { user } = useAuth();
  const [termino, setTermino] = useState('');
  const [soloBajo, setSoloBajo] = useState(false);
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);

  const cargar = async () => {
    if (!user?.sucursal_id) return;
    setLoading(true);
    try {
      const r = await inventarioService.disponibilidad(user.sucursal_id, termino, soloBajo);
      setData(r);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { cargar(); /* eslint-disable-next-line */ }, [user?.sucursal_id, soloBajo]);

  return (
    <div className="space-y-3">
      <div className="card flex flex-wrap gap-3 items-end">
        <div className="flex-1 min-w-[200px]">
          <label className="label">Buscar</label>
          <input className="input" value={termino} onChange={(e) => setTermino(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && cargar()} />
        </div>
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={soloBajo} onChange={(e) => setSoloBajo(e.target.checked)} /> Solo bajo mínimo
        </label>
        <button className="btn-primary" onClick={cargar}>Buscar</button>
      </div>
      <div className="card p-0">
        <Tabla
          loading={loading}
          data={data}
          emptyText="No hay productos"
          columns={[
            { key: 'sku', header: 'SKU', width: '120px' },
            { key: 'nombre', header: 'Producto' },
            { key: 'cantidad', header: 'Stock', render: (r) => (
              <span className={r.alerta_stock_bajo ? 'text-red-600 font-bold' : ''}>
                {formatNumber(r.cantidad)}
              </span>
            )},
            { key: 'stock_minimo', header: 'Mínimo', render: (r) => formatNumber(r.stock_minimo) },
            { key: 'estado', header: 'Estado', render: (r) => (
              r.alerta_stock_bajo
                ? <span className="px-2 py-1 bg-red-100 text-red-700 text-xs rounded">⚠ Bajo</span>
                : <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded">OK</span>
            )},
          ]}
        />
      </div>
    </div>
  );
}
