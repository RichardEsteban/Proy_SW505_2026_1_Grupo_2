import { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import adminService from '@modules/admin/services/adminService.js';
import Tabla from '@shared/components/Tabla.jsx';

export default function Clientes() {
  const [data, setData] = useState([]);
  const [form, setForm] = useState({ tipo_documento: 'DNI', numero_documento: '', nombre: '' });
  const [loading, setLoading] = useState(false);

  const cargar = async () => {
    setLoading(true);
    try { setData(await adminService.listarClientes()); } finally { setLoading(false); }
  };
  useEffect(() => { cargar(); }, []);

  const crear = async () => {
    try {
      await adminService.crearCliente(form);
      toast.success('Cliente creado');
      cargar();
    } catch (e) { toast.error(e.response?.data?.detail || 'Error'); }
  };

  return (
    <div className="space-y-3">
      <div className="card grid grid-cols-1 md:grid-cols-4 gap-2">
        <select className="input" value={form.tipo_documento} onChange={(e) => setForm({ ...form, tipo_documento: e.target.value })}>
          <option>DNI</option><option>RUC</option>
        </select>
        <input className="input" placeholder="Nro documento" value={form.numero_documento} onChange={(e) => setForm({ ...form, numero_documento: e.target.value })} />
        <input className="input" placeholder="Nombre" value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} />
        <button className="btn-primary" onClick={crear}>Crear cliente</button>
      </div>
      <div className="card p-0">
        <Tabla loading={loading} data={data} emptyText="Sin clientes" columns={[
          { key: 'tipo_documento', header: 'Tipo' },
          { key: 'numero_documento', header: 'Nro' },
          { key: 'nombre', header: 'Nombre' },
        ]} />
      </div>
    </div>
  );
}
