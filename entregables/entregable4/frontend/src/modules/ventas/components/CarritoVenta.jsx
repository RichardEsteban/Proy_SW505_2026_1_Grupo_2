import { formatCurrency } from '@shared/utils/formatCurrency.js';

export default function CarritoVenta({ items, onQuitar, onCantidad }) {
  if (!items.length) {
    return <div className="text-center text-gray-400 py-12">🛒 Carrito vacío</div>;
  }
  return (
    <div className="divide-y">
      {items.map((it) => (
        <div key={it.producto_id} className="flex items-center gap-3 p-3">
          <div className="flex-1">
            <div className="font-medium text-sm">{it.nombre}</div>
            <div className="text-xs text-gray-500">SKU: {it.sku} · {formatCurrency(it.precio_unitario)} c/u</div>
          </div>
          <input
            type="number"
            min="1"
            step="1"
            value={it.cantidad}
            onChange={(e) => onCantidad(it.producto_id, parseFloat(e.target.value) || 1)}
            className="w-20 input text-center"
          />
          <div className="w-24 text-right font-semibold">{formatCurrency(it.cantidad * it.precio_unitario)}</div>
          <button onClick={() => onQuitar(it.producto_id)} className="text-red-500 hover:text-red-700 px-2">✕</button>
        </div>
      ))}
    </div>
  );
}
