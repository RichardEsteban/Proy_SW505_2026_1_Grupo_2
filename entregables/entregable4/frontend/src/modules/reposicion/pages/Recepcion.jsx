import { useEffect, useState } from 'react';
import reposicionService from '@modules/reposicion/services/reposicionService.js';
import Tabla from '@shared/components/Tabla.jsx';
import { formatDate } from '@shared/utils/formatCurrency.js';

export default function Recepcion() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);

  const cargar = async () => {
    setLoading(true);
    try {
      const r = await reposicionService.listarSolicitudes({ estado: 'EN_TRANSITO' });
      setData(r);
    } finally { setLoading(false); }
  };

  useEffect(() => { cargar(); }, []);

  return (
    <div className="space-y-3">
      <h2 className="text-xl font-bold">Recepciones pendientes</h2>
      <div className="card p-0">
        <Tabla
          loading={loading}
          data={data}
          emptyText="No hay recepciones pendientes"
          columns={[
            { key: 'codigo', header: 'Código' },
            { key: 'sucursal_origen_id', header: 'Sucursal' },
            { key: 'almacen_destino_id', header: 'Almacén' },
            { key: 'fecha_solicitud', header: 'Fecha', render: (r) => formatDate(r.fecha_solicitud) },
          ]}
        />
      </div>
    </div>
  );
}
