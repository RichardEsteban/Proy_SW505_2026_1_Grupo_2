import { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import adminService from '@modules/admin/services/adminService.js';
import Tabla from '@shared/components/Tabla.jsx';

export default function Proveedores() {
  const [data, setData] = useState([]);
  const [form, setForm] = useState({ ruc: '', razon_social: '', nombre_comercial: '' });
  const [loading, setLoading] = useState(false);

  const cargar = async () => {
    setLoading(true);
    try { setData(await adminService.listarProveedores()); } finally { setLoading(false); }
  };
  useEffect(() => { cargar(); }, []);

  const crear = async () => {
    try {
      await adminService.crearProveedor(form);
      toast.success('Proveedor creado');
      cargar();
    } catch (e) { toast.error(e.response?.data?.detail || 'Error'); }
  };

  return (
    <div className="space-y-3">
      <div className="card grid grid-cols-1 md:grid-cols-4 gap-2">
        <input className="input" placeholder="RUC" value={form.ruc} onChange={(e) => setForm({ ...form, ruc: e.target.value })} />
        <input className="input" placeholder="Razón social" value={form.razon_social} onChange={(e) => setForm({ ...form, razon_social: e.target.value })} />
        <input className="input" placeholder="Nombre comercial" value={form.nombre_comercial} onChange={(e) => setForm({ ...form, nombre_comercial: e.target.value })} />
        <button className="btn-primary" onClick={crear}>Crear</button>
      </div>
      <div className="card p-0">
        <Tabla loading={loading} data={data} emptyText="Sin proveedores" columns={[
          { key: 'ruc', header: 'RUC' },
          { key: 'razon_social', header: 'Razón Social' },
          { key: 'nombre_comercial', header: 'Comercial' },
        ]} />
      </div>
    </div>
  );
}
