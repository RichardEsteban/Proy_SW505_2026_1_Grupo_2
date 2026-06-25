export default function ComprobanteModal({ abierto, onCerrar, venta, pdfUrl }) {
  if (!abierto) return null;
  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50">
      <div className="card w-full max-w-md text-center">
        <h2 className="text-xl font-bold mb-2 text-green-600">✓ Venta registrada</h2>
        <p className="text-sm text-gray-500 mb-1">Comprobante</p>
        <p className="text-lg font-semibold mb-3">{venta?.serie}-{venta?.numero}</p>
        <p className="text-2xl font-bold text-primary-700 mb-4">S/ {venta?.total?.toFixed(2)}</p>
        {pdfUrl && (
          <a href={pdfUrl} target="_blank" rel="noreferrer" className="btn-primary mb-2">📄 Ver PDF</a>
        )}
        <div>
          <button className="btn-secondary w-full" onClick={onCerrar}>Cerrar</button>
        </div>
      </div>
    </div>
  );
}
