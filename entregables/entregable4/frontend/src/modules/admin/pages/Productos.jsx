import { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import adminService from '@modules/admin/services/adminService.js';
import Tabla from '@shared/components/Tabla.jsx';
import { formatCurrency } from '@shared/utils/formatCurrency.js';

export default function Productos() {
  const [data, setData] = useState([]);
  const [form, setForm] = useState({ sku: '', nombre: '', precio_compra: 0, precio_venta: 0, codigo_barra: '' });
  const [loading, setLoading] = useState(false);

  const cargar = async () => {
    setLoading(true);
    try { setData(await adminService.listarProductos()); } finally { setLoading(false); }
  };
  useEffect(() => { cargar(); }, []);

  const crear = async () => {
    try {
      await adminService.crearProducto({ ...form, precio_compra: parseFloat(form.precio_compra), precio_venta: parseFloat(form.precio_venta) });
      toast.success('Producto creado');
      setForm({ sku: '', nombre: '', precio_compra: 0, precio_venta: 0, codigo_barra: '' });
      cargar();
    } catch (e) { toast.error(e.response?.data?.detail || 'Error'); }
  };

  return (
    <div className="space-y-3">
      <div className="card grid grid-cols-1 md:grid-cols-5 gap-2">
        <input className="input" placeholder="SKU" value={form.sku} onChange={(e) => setForm({ ...form, sku: e.target.value })} />
        <input className="input md:col-span-2" placeholder="Nombre" value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} />
        <input className="input" type="number" step="0.01" placeholder="Compra" value={form.precio_compra} onChange={(e) => setForm({ ...form, precio_compra: e.target.value })} />
        <input className="input" type="number" step="0.01" placeholder="Venta" value={form.precio_venta} onChange={(e) => setForm({ ...form, precio_venta: e.target.value })} />
        <button className="btn-primary md:col-span-5" onClick={crear}>Crear producto</button>
      </div>
      <div className="card p-0">
        <Tabla
          loading={loading}
          data={data}
          emptyText="Sin productos"
          columns={[
            { key: 'sku', header: 'SKU' },
            { key: 'nombre', header: 'Nombre' },
            { key: 'precio_venta', header: 'Precio', render: (r) => formatCurrency(r.precio_venta) },
            { key: 'activo', header: 'Estado', render: (r) => r.activo ? '✓' : '✕' },
          ]}
        />
      </div>
    </div>
  );
}
