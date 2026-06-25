/**
 * Tabla genérica. columns = [{ key, header, render? }]
 */
export default function Tabla({ columns = [], data = [], loading = false, emptyText = 'Sin datos' }) {
  if (loading) {
    return <div className="text-center py-8 text-gray-500">Cargando...</div>;
  }
  if (!data.length) {
    return <div className="text-center py-8 text-gray-400">{emptyText}</div>;
  }
  return (
    <div className="overflow-x-auto rounded-lg border border-gray-200">
      <table className="min-w-full divide-y divide-gray-200 text-sm">
        <thead className="bg-gray-50">
          <tr>
            {columns.map((c) => (
              <th
                key={c.key}
                className="px-4 py-3 text-left font-semibold text-gray-700"
                style={c.width ? { width: c.width } : undefined}
              >
                {c.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100 bg-white">
          {data.map((row, i) => (
            <tr key={row.id ?? i} className="hover:bg-gray-50">
              {columns.map((c) => (
                <td key={c.key} className="px-4 py-3 text-gray-800">
                  {c.render ? c.render(row) : row[c.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
