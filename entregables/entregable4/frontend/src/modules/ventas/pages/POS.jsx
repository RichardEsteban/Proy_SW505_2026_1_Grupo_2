import { useState, useMemo } from 'react';
import toast from 'react-hot-toast';
import BuscadorProducto from '@modules/ventas/components/BuscadorProducto.jsx';
import CarritoVenta from '@modules/ventas/components/CarritoVenta.jsx';
import ModalCliente from '@modules/ventas/components/ModalCliente.jsx';
import ComprobanteModal from '@modules/ventas/components/ComprobanteModal.jsx';
import ventaService from '@modules/ventas/services/ventaService.js';
import { formatCurrency } from '@shared/utils/formatCurrency.js';
import { useAuth } from '@shared/hooks/useAuth.js';

export default function POS() {
  const { user } = useAuth();
  const [items, setItems] = useState([]);
  const [cliente, setCliente] = useState(null);
  const [tipo, setTipo] = useState('BOLETA');
  const [serie, setSerie] = useState('B001');
  const [modalCliente, setModalCliente] = useState(false);
  const [modalComp, setModalComp] = useState(false);
  const [ventaHecha, setVentaHecha] = useState(null);
  const [pdfUrl, setPdfUrl] = useState(null);
  const [procesando, setProcesando] = useState(false);

  const agregar = (p) => {
    setItems((prev) => {
      const ex = prev.find((x) => x.producto_id === p.id);
      if (ex) return prev.map((x) => x.producto_id === p.id ? { ...x, cantidad: x.cantidad + 1 } : x);
      return [...prev, {
        producto_id: p.id, nombre: p.nombre, sku: p.sku,
        cantidad: 1, precio_unitario: p.precio_venta, descuento: 0,
      }];
    });
  };

  const quitar = (id) => setItems((prev) => prev.filter((x) => x.producto_id !== id));
  const cambiarCant = (id, c) => setItems((prev) => prev.map((x) => x.producto_id === id ? { ...x, cantidad: c } : x));

  const totales = useMemo(() => {
    const total = items.reduce((acc, it) => acc + it.cantidad * it.precio_unitario, 0);
    const igv = total * 18 / 118;
    const subtotal = total - igv;
    return { total, igv, subtotal };
  }, [items]);

  const cobrar = async () => {
    if (!items.length) return toast.error('Carrito vacío');
    setProcesando(true);
    try {
      const numero = String(Date.now()).slice(-8);
      const r = await ventaService.registrar({
        serie, numero, tipo_comprobante: tipo,
        sucursal_id: user.sucursal_id,
        cliente_id: cliente?.id || null,
        items: items.map((it) => ({
          producto_id: it.producto_id, cantidad: it.cantidad,
          precio_unitario: it.precio_unitario, descuento: it.descuento,
        })),
      });
      toast.success('Venta registrada');
      setVentaHecha(r);
      // Generar PDF
      try {
        const pdf = await ventaService.generarComprobante(r.id);
        setPdfUrl(pdf.pdf_url);
      } catch {}
      setModalComp(true);
      setItems([]);
      setCliente(null);
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Error al registrar venta');
    } finally {
      setProcesando(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <div className="lg:col-span-2 space-y-3">
        <div className="card">
          <BuscadorProducto onAgregar={agregar} />
        </div>
        <div className="card p-0">
          <CarritoVenta items={items} onQuitar={quitar} onCantidad={cambiarCant} />
        </div>
      </div>
      <div className="space-y-3">
        <div className="card">
          <h3 className="font-semibold mb-2">Comprobante</h3>
          <div className="grid grid-cols-2 gap-2">
            <select className="input" value={tipo} onChange={(e) => { setTipo(e.target.value); setSerie(e.target.value === 'FACTURA' ? 'F001' : 'B001'); }}>
              <option>BOLETA</option><option>FACTURA</option><option>TICKET</option>
            </select>
            <input className="input" value={serie} onChange={(e) => setSerie(e.target.value)} />
          </div>
          <div className="mt-3">
            <label className="label">Cliente</label>
            <button onClick={() => setModalCliente(true)} className="btn-secondary w-full text-left">
              {cliente ? cliente.nombre : '+ Seleccionar cliente'}
            </button>
          </div>
        </div>
        <div className="card bg-gray-50">
          <div className="flex justify-between text-sm py-1">
            <span>Subtotal</span><span>{formatCurrency(totales.subtotal)}</span>
          </div>
          <div className="flex justify-between text-sm py-1">
            <span>IGV (18%)</span><span>{formatCurrency(totales.igv)}</span>
          </div>
          <div className="flex justify-between text-lg font-bold py-2 border-t mt-2">
            <span>TOTAL</span><span className="text-primary-700">{formatCurrency(totales.total)}</span>
          </div>
          <button onClick={cobrar} disabled={procesando || !items.length} className="btn-primary w-full mt-3">
            {procesando ? 'Procesando...' : '💰 Cobrar'}
          </button>
        </div>
      </div>
      <ModalCliente abierto={modalCliente} onCerrar={() => setModalCliente(false)} onSeleccionar={setCliente} />
      <ComprobanteModal abierto={modalComp} onCerrar={() => setModalComp(false)} venta={ventaHecha} pdfUrl={pdfUrl} />
    </div>
  );
}
