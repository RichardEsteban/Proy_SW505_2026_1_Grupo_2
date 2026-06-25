import { useEffect, useState } from 'react';
import sucursalService from '@modules/sucursal/services/sucursalService.js';
import { useAuth } from '@shared/hooks/useAuth.js';
import { formatCurrency } from '@shared/utils/formatCurrency.js';

export default function DashboardSucursal() {
  const { user } = useAuth();
  const [data, setData] = useState(null);
  useEffect(() => { sucursalService.dashboard(user?.sucursal_id).then(setData).catch(() => {}); }, [user?.sucursal_id]);

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
      <KPI titulo="Ventas 30d" valor={data ? formatCurrency(data.kpi_ventas_30d?.total) : '—'} />
      <KPI titulo="Items bajo mínimo" valor={data?.kpi_inventario?.items_bajo_minimo ?? '—'} />
      <KPI titulo="Alertas activas" valor={data?.alertas_activas ?? '—'} />
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
