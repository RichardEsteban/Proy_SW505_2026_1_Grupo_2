import { useEffect, useState } from 'react';
import adminService from '@modules/admin/services/adminService.js';
import Tabla from '@shared/components/Tabla.jsx';

export default function Ubicaciones() {
  const [sucursales, setSucursales] = useState([]);
  const [almacenes, setAlmacenes] = useState([]);
  const [s, setS] = useState({ codigo: '', nombre: '', direccion: '' });
  const [a, setA] = useState({ codigo: '', nombre: '', direccion: '' });

  const cargar = async () => {
    setSucursales(await adminService.listarSucursales());
    setAlmacenes(await adminService.listarAlmacenes());
  };
  useEffect(() => { cargar(); }, []);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div className="space-y-3">
        <div className="card grid grid-cols-1 gap-2">
          <h3 className="font-bold">Nueva sucursal</h3>
          <input className="input" placeholder="Código" value={s.codigo} onChange={(e) => setS({ ...s, codigo: e.target.value })} />
          <input className="input" placeholder="Nombre" value={s.nombre} onChange={(e) => setS({ ...s, nombre: e.target.value })} />
          <input className="input" placeholder="Dirección" value={s.direccion} onChange={(e) => setS({ ...s, direccion: e.target.value })} />
          <button className="btn-primary" onClick={async () => { await adminService.crearSucursal(s); cargar(); }}>Crear</button>
        </div>
        <div className="card p-0">
          <Tabla data={sucursales} columns={[
            { key: 'codigo', header: 'Código' },
            { key: 'nombre', header: 'Nombre' },
            { key: 'activo', header: 'Estado' },
          ]} />
        </div>
      </div>
      <div className="space-y-3">
        <div className="card grid grid-cols-1 gap-2">
          <h3 className="font-bold">Nuevo almacén</h3>
          <input className="input" placeholder="Código" value={a.codigo} onChange={(e) => setA({ ...a, codigo: e.target.value })} />
          <input className="input" placeholder="Nombre" value={a.nombre} onChange={(e) => setA({ ...a, nombre: e.target.value })} />
          <input className="input" placeholder="Dirección" value={a.direccion} onChange={(e) => setA({ ...a, direccion: e.target.value })} />
          <button className="btn-primary" onClick={async () => { await adminService.crearAlmacen(a); cargar(); }}>Crear</button>
        </div>
        <div className="card p-0">
          <Tabla data={almacenes} columns={[
            { key: 'codigo', header: 'Código' },
            { key: 'nombre', header: 'Nombre' },
            { key: 'activo', header: 'Estado' },
          ]} />
        </div>
      </div>
    </div>
  );
}
