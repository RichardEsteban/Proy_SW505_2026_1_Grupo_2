import { useState, useEffect } from 'react';
import adminService from '@modules/admin/services/adminService.js';

export default function ModalCliente({ abierto, onCerrar, onSeleccionar }) {
  const [termino, setTermino] = useState('');
  const [clientes, setClientes] = useState([]);
  const [nuevo, setNuevo] = useState({ tipo_documento: 'DNI', numero_documento: '', nombre: '' });

  useEffect(() => {
    if (!abierto) return;
    adminService.listarClientes(termino).then(setClientes).catch(() => setClientes([]));
  }, [termino, abierto]);

  if (!abierto) return null;

  const crear = async () => {
    if (!nuevo.numero_documento || !nuevo.nombre) return;
    try {
      const c = await adminService.crearCliente(nuevo);
      onSeleccionar(c);
      onCerrar();
    } catch (e) {
      alert('Error al crear cliente');
    }
  };

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50">
      <div className="card w-full max-w-2xl max-h-[80vh] overflow-auto">
        <h2 className="text-lg font-bold mb-3">Seleccionar cliente</h2>
        <input className="input mb-3" placeholder="Buscar por nombre o documento" value={termino} onChange={(e) => setTermino(e.target.value)} />
        <div className="max-h-48 overflow-auto border rounded mb-4">
          {clientes.map((c) => (
            <button key={c.id} onClick={() => { onSeleccionar(c); onCerrar(); }} className="w-full text-left p-2 hover:bg-gray-50 border-b">
              <div className="font-medium">{c.nombre}</div>
              <div className="text-xs text-gray-500">{c.tipo_documento}: {c.numero_documento}</div>
            </button>
          ))}
        </div>
        <div className="border-t pt-3">
          <h3 className="font-semibold text-sm mb-2">Crear nuevo cliente rápido</h3>
          <div className="grid grid-cols-3 gap-2">
            <select className="input" value={nuevo.tipo_documento} onChange={(e) => setNuevo({ ...nuevo, tipo_documento: e.target.value })}>
              <option>DNI</option><option>RUC</option>
            </select>
            <input className="input" placeholder="Nro doc" value={nuevo.numero_documento} onChange={(e) => setNuevo({ ...nuevo, numero_documento: e.target.value })} />
            <input className="input" placeholder="Nombre" value={nuevo.nombre} onChange={(e) => setNuevo({ ...nuevo, nombre: e.target.value })} />
          </div>
          <div className="flex justify-end gap-2 mt-3">
            <button className="btn-secondary" onClick={onCerrar}>Cancelar</button>
            <button className="btn-primary" onClick={crear}>Crear y usar</button>
          </div>
        </div>
      </div>
    </div>
  );
}
