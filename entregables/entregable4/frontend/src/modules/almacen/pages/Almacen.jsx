import { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import almacenService from '@modules/almacen/services/almacenService.js';
import adminService from '@modules/admin/services/adminService.js';
import Tabla from '@shared/components/Tabla.jsx';

export default function Almacen() {
  const [almacenes, setAlmacenes] = useState([]);
  const [productos, setProductos] = useState([]);
  const [form, setForm] = useState({ almacen_id: '', observacion: '', items: [{ producto_id: '', cantidad: 1 }] });

  useEffect(() => {
    almacenService.listarAlmacenes().then(setAlmacenes);
    adminService.listarProductos().then(setProductos);
  }, []);

  const enviar = async () => {
    if (!form.almacen_id) return toast.error('Selecciona almacén');
    try {
      await almacenService.registrarEntrada({
        ...form,
        items: form.items.map((i) => ({ producto_id: parseInt(i.producto_id), cantidad: parseFloat(i.cantidad) })),
      });
      toast.success('Entrada registrada');
      setForm({ almacen_id: '', observacion: '', items: [{ producto_id: '', cantidad: 1 }] });
    } catch (e) { toast.error(e.response?.data?.detail || 'Error'); }
  };

  return (
    <div className="card max-w-2xl space-y-3">
      <h2 className="text-xl font-bold">Entrada manual a almacén</h2>
      <div>
        <label className="label">Almacén</label>
        <select className="input" value={form.almacen_id} onChange={(e) => setForm({ ...form, almacen_id: e.target.value })}>
          <option value="">-- Selecciona --</option>
          {almacenes.map((a) => <option key={a.id} value={a.id}>{a.nombre}</option>)}
        </select>
      </div>
      <div>
        <label className="label">Observación</label>
        <input className="input" value={form.observacion} onChange={(e) => setForm({ ...form, observacion: e.target.value })} />
      </div>
      <div className="space-y-2">
        {form.items.map((it, idx) => (
          <div key={idx} className="grid grid-cols-[1fr_120px_40px] gap-2">
            <select className="input" value={it.producto_id} onChange={(e) => setForm({ ...form, items: form.items.map((x, i) => i === idx ? { ...x, producto_id: e.target.value } : x) })}>
              <option value="">-- Producto --</option>
              {productos.map((p) => <option key={p.id} value={p.id}>{p.nombre}</option>)}
            </select>
            <input className="input" type="number" min="0.01" step="0.01" value={it.cantidad} onChange={(e) => setForm({ ...form, items: form.items.map((x, i) => i === idx ? { ...x, cantidad: e.target.value } : x) })} />
            <button className="btn-secondary" onClick={() => setForm({ ...form, items: form.items.filter((_, i) => i !== idx) })} disabled={form.items.length === 1}>✕</button>
          </div>
        ))}
        <button className="btn-secondary" onClick={() => setForm({ ...form, items: [...form.items, { producto_id: '', cantidad: 1 }] })}>+ Item</button>
      </div>
      <button className="btn-primary" onClick={enviar}>Registrar entrada</button>
    </div>
  );
}
