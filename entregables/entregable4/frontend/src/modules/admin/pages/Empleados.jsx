import { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import adminService from '@modules/admin/services/adminService.js';
import Tabla from '@shared/components/Tabla.jsx';

export default function Empleados() {
  const [data, setData] = useState([]);
  const [form, setForm] = useState({ dni: '', nombre: '', apellido: '', email: '', username: '', password: '', rol_id: 2, sucursal_id: '' });
  const [loading, setLoading] = useState(false);

  const cargar = async () => {
    setLoading(true);
    try { setData(await adminService.listarUsuarios()); } finally { setLoading(false); }
  };
  useEffect(() => { cargar(); }, []);

  const crear = async () => {
    try {
      await adminService.crearUsuario({ ...form, rol_id: parseInt(form.rol_id), sucursal_id: form.sucursal_id ? parseInt(form.sucursal_id) : null });
      toast.success('Empleado creado');
      cargar();
    } catch (e) { toast.error(e.response?.data?.detail || 'Error'); }
  };

  return (
    <div className="space-y-3">
      <div className="card grid grid-cols-1 md:grid-cols-4 gap-2">
        <input className="input" placeholder="DNI" value={form.dni} onChange={(e) => setForm({ ...form, dni: e.target.value })} />
        <input className="input" placeholder="Nombre" value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} />
        <input className="input" placeholder="Apellido" value={form.apellido} onChange={(e) => setForm({ ...form, apellido: e.target.value })} />
        <input className="input" placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
        <input className="input" placeholder="Username" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} />
        <input className="input" placeholder="Password" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
        <input className="input" placeholder="Rol ID (1=Admin)" type="number" value={form.rol_id} onChange={(e) => setForm({ ...form, rol_id: e.target.value })} />
        <input className="input" placeholder="Sucursal ID" type="number" value={form.sucursal_id} onChange={(e) => setForm({ ...form, sucursal_id: e.target.value })} />
        <button className="btn-primary md:col-span-4" onClick={crear}>Crear empleado</button>
      </div>
      <div className="card p-0">
        <Tabla
          loading={loading}
          data={data}
          emptyText="Sin empleados"
          columns={[
            { key: 'dni', header: 'DNI' },
            { key: 'username', header: 'Usuario' },
            { key: 'nombre_completo', header: 'Nombre' },
            { key: 'email', header: 'Email' },
            { key: 'rol_id', header: 'Rol' },
            { key: 'estado', header: 'Estado' },
          ]}
        />
      </div>
    </div>
  );
}
