import { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import reposicionService from '@modules/reposicion/services/reposicionService.js';
import adminService from '@modules/admin/services/adminService.js';
import Tabla from '@shared/components/Tabla.jsx';
import { useAuth } from '@shared/hooks/useAuth.js';
import { formatDate } from '@shared/utils/formatCurrency.js';

export default function Solicitudes() {
  const { user } = useAuth();
  const [solicitudes, setSolicitudes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({ sucursal_origen_id: user?.sucursal_id, almacen_destino_id: '', motivo: '', items: [{ producto_id: '', cantidad: 1 }] });
  const [productos, setProductos] = useState([]);

  const cargar = async () => {
    setLoading(true);
    try {
      const r = await reposicionService.listarSolicitudes();
      setSolicitudes(r);
    } finally { setLoading(false); }
  };

  useEffect(() => { cargar(); adminService.listarProductos().then(setProductos); }, []);

  const enviar = async () => {
    if (!form.almacen_destino_id) return toast.error('Selecciona almacén');
    if (form.items.some((i) => !i.producto_id)) return toast.error('Completa items');
    try {
      await reposicionService.crearSolicitud({
        ...form,
        items: form.items.map((i) => ({ producto_id: parseInt(i.producto_id), cantidad: parseFloat(i.cantidad) })),
      });
      toast.success('Solicitud creada');
      cargar();
    } catch (e) { toast.error(e.response?.data?.detail || 'Error'); }
  };

  const accion = async (id, tipo) => {
    try {
      if (tipo === 'aprobar') await reposicionService.evaluar(id, 'aprobar');
      if (tipo === 'rechazar') await reposicionService.evaluar(id, 'rechazar', 'Rechazada');
      if (tipo === 'enviar') await reposicionService.enviar(id);
      if (tipo === 'recibir') await reposicionService.recibir(id);
      toast.success('OK');
      cargar();
    } catch (e) { toast.error(e.response?.data?.detail || 'Error'); }
  };

  return (
    <div className="space-y-4">
      <div className="card">
        <h2 className="font-bold mb-3">Nueva solicitud</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div><label className="label">Almacén destino</label><input className="input" type="number" value={form.almacen_destino_id} onChange={(e) => setForm({ ...form, almacen_destino_id: e.target.value })} /></div>
          <div className="md:col-span-2"><label className="label">Motivo</label><input className="input" value={form.motivo} onChange={(e) => setForm({ ...form, motivo: e.target.value })} /></div>
        </div>
        <div className="mt-3 space-y-2">
          {form.items.map((it, idx) => (
            <div key={idx} className="grid grid-cols-[1fr_120px_40px] gap-2">
              <select className="input" value={it.producto_id} onChange={(e) => setForm({ ...form, items: form.items.map((x, i) => i === idx ? { ...x, producto_id: e.target.value } : x) })}>
                <option value="">-- Producto --</option>
                {productos.map((p) => <option key={p.id} value={p.id}>{p.nombre} ({p.sku})</option>)}
              </select>
              <input className="input" type="number" min="1" step="0.01" value={it.cantidad} onChange={(e) => setForm({ ...form, items: form.items.map((x, i) => i === idx ? { ...x, cantidad: e.target.value } : x) })} />
              <button className="btn-secondary" onClick={() => setForm({ ...form, items: form.items.filter((_, i) => i !== idx) })} disabled={form.items.length === 1}>✕</button>
            </div>
          ))}
        </div>
        <div className="flex justify-between mt-3">
          <button className="btn-secondary" onClick={() => setForm({ ...form, items: [...form.items, { producto_id: '', cantidad: 1 }] })}>+ Item</button>
          <button className="btn-primary" onClick={enviar}>Crear solicitud</button>
        </div>
      </div>
      <div className="card p-0">
        <Tabla
          loading={loading}
          data={solicitudes}
          emptyText="Sin solicitudes"
          columns={[
            { key: 'codigo', header: 'Código' },
            { key: 'estado', header: 'Estado', render: (r) => <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded">{r.estado}</span> },
            { key: 'fecha_solicitud', header: 'Fecha', render: (r) => formatDate(r.fecha_solicitud) },
            { key: 'acciones', header: 'Acciones', render: (r) => (
              <div className="flex gap-1">
                {r.estado === 'PENDIENTE' && <>
                  <button onClick={() => accion(r.id, 'aprobar')} className="text-xs px-2 py-1 bg-green-100 text-green-700 rounded">Aprobar</button>
                  <button onClick={() => accion(r.id, 'rechazar')} className="text-xs px-2 py-1 bg-red-100 text-red-700 rounded">Rechazar</button>
                </>}
                {r.estado === 'APROBADA' && <button onClick={() => accion(r.id, 'enviar')} className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded">Enviar</button>}
                {r.estado === 'EN_TRANSITO' && <button onClick={() => accion(r.id, 'recibir')} className="text-xs px-2 py-1 bg-emerald-100 text-emerald-700 rounded">Recibir</button>}
              </div>
            )},
          ]}
        />
      </div>
    </div>
  );
}
