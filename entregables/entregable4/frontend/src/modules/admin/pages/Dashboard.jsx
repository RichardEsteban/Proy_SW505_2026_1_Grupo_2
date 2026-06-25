import { useEffect, useState } from 'react';
import sucursalService from '@modules/sucursal/services/sucursalService.js';
import { formatCurrency } from '@shared/utils/formatCurrency.js';

export default function Dashboard() {
  const [data, setData] = useState(null);
  useEffect(() => { sucursalService.dashboard().then(setData).catch(() => {}); }, []);

  const v = data?.kpi_ventas_30d;
  const i = data?.kpi_inventario;
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
        <KPI titulo="Ventas 30d" valor={v ? formatCurrency(v.total) : '—'} sub={v ? `${v.cantidad_ventas} ventas` : ''} />
        <KPI titulo="Ticket promedio" valor={v ? formatCurrency(v.ticket_promedio) : '—'} />
        <KPI titulo="IGV recaudado" valor={v ? formatCurrency(v.igv) : '—'} />
        <KPI titulo="Items bajo mínimo" valor={i?.items_bajo_minimo ?? '—'} />
      </div>
    </div>
  );
}

function KPI({ titulo, valor, sub }) {
  return (
    <div className="card">
      <div className="text-xs text-gray-500 uppercase">{titulo}</div>
      <div className="text-2xl font-bold mt-1">{valor}</div>
      {sub && <div className="text-xs text-gray-400 mt-1">{sub}</div>}
    </div>
  );
}
