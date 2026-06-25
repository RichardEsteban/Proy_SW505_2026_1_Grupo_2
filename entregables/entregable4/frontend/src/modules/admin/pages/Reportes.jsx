import { useState } from 'react';
import api from '@shared/utils/api.js';
import { formatCurrency } from '@shared/utils/formatCurrency.js';

export default function Reportes() {
  const [desde, setDesde] = useState(new Date(Date.now() - 30 * 86400000).toISOString().slice(0, 10));
  const [hasta, setHasta] = useState(new Date().toISOString().slice(0, 10));
  const [data, setData] = useState(null);

  const generar = async () => {
    const r = await api.get('/reportes/ventas', { params: { fecha_desde: desde, fecha_hasta: hasta } });
    setData(r.data);
  };

  return (
    <div className="space-y-3">
      <div className="card grid grid-cols-1 md:grid-cols-3 gap-2 items-end">
        <div><label className="label">Desde</label><input className="input" type="date" value={desde} onChange={(e) => setDesde(e.target.value)} /></div>
        <div><label className="label">Hasta</label><input className="input" type="date" value={hasta} onChange={(e) => setHasta(e.target.value)} /></div>
        <button className="btn-primary" onClick={generar}>Generar</button>
      </div>
      {data && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          <KPI titulo="Ventas" valor={data.cantidad_ventas} />
          <KPI titulo="Total" valor={formatCurrency(data.total)} />
          <KPI titulo="IGV" valor={formatCurrency(data.igv)} />
          <KPI titulo="Ticket prom." valor={formatCurrency(data.ticket_promedio)} />
        </div>
      )}
    </div>
  );
}

function KPI({ titulo, valor }) {
  return (
    <div className="card">
      <div className="text-xs text-gray-500 uppercase">{titulo}</div>
      <div className="text-2xl font-bold mt-1">{valor}</div>
    </div>
  );
}
