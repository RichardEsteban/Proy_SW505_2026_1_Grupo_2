import { useEffect, useMemo, useState } from 'react'
import { listarAlertas, marcarAlertaComoLeida } from '@/shared/api/alertaApi'
import { useAuth } from '@/shared/auth/AuthContext'
import Alert from '@/shared/components/Alert'
import Badge from '@/shared/components/Badge'
import Button from '@/shared/components/Button'
import Card from '@/shared/components/Card'
import Input from '@/shared/components/Input'
import Loader from '@/shared/components/Loader'
import PageHeader from '@/shared/components/PageHeader'
import Select from '@/shared/components/Select'
import Table from '@/shared/components/Table'
import { formatDateTime } from '@/shared/utils/roleViews'

function tipoLabel(tipo) {
  if (tipo === 'STOCK_AGOTADO') return 'Sin stock'
  if (tipo === 'STOCK_MINIMO') return 'Stock mínimo'
  return tipo || '-'
}

function tipoTone(tipo) {
  if (tipo === 'STOCK_AGOTADO') return 'red'
  if (tipo === 'STOCK_MINIMO') return 'amber'
  return 'slate'
}

export default function AlertasStockPage() {
  const { usuario } = useAuth()
  const [alertas, setAlertas] = useState([])
  const [estado, setEstado] = useState('PENDIENTE')
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  async function loadData() {
    setError('')
    try {
      const data = await listarAlertas({ idUbicacion: usuario?.idUbicacion, estado: estado || undefined })
      setAlertas(data)
    } catch (err) {
      setError(err.message || 'No se pudieron cargar las alertas de stock')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [usuario?.idUbicacion, estado])

  const filtered = useMemo(() => {
    const term = search.trim().toLowerCase()
    if (!term) return alertas
    return alertas.filter((item) => [item.producto, item.ubicacion, item.tipoAlerta, item.estado]
      .some((value) => String(value || '').toLowerCase().includes(term)))
  }, [alertas, search])

  const resumen = useMemo(() => ({
    total: filtered.length,
    pendientes: filtered.filter((item) => item.estado === 'PENDIENTE').length,
    minimo: filtered.filter((item) => item.tipoAlerta === 'STOCK_MINIMO').length,
    agotado: filtered.filter((item) => item.tipoAlerta === 'STOCK_AGOTADO').length
  }), [filtered])

  async function handleLeer(row) {
    setActionLoading(true)
    setError('')
    setSuccess('')
    try {
      await marcarAlertaComoLeida(row.idAlerta)
      setSuccess('Alerta marcada como leída.')
      await loadData()
    } catch (err) {
      setError(err.message || 'No se pudo marcar la alerta como leída')
    } finally {
      setActionLoading(false)
    }
  }

  const columns = [
    { key: 'producto', header: 'Producto', render: (row) => <span className="font-semibold text-slate-950">{row.producto}</span> },
    { key: 'tipoAlerta', header: 'Tipo', render: (row) => <Badge tone={tipoTone(row.tipoAlerta)}>{tipoLabel(row.tipoAlerta)}</Badge> },
    { key: 'cantidadActual', header: 'Stock actual', render: (row) => <span className="font-bold text-slate-950">{row.cantidadActual}</span> },
    { key: 'stockReferencia', header: 'Stock mínimo' },
    { key: 'fechaCreacion', header: 'Fecha', render: (row) => formatDateTime(row.fechaCreacion) },
    { key: 'estado', header: 'Estado', render: (row) => <Badge tone={row.estado === 'PENDIENTE' ? 'amber' : 'green'}>{row.estado === 'PENDIENTE' ? 'Pendiente' : 'Leída'}</Badge> },
    {
      key: 'acciones',
      header: 'Acciones',
      className: 'text-right',
      render: (row) => row.estado === 'PENDIENTE'
        ? <Button type="button" variant="secondary" className="px-3 py-2" disabled={actionLoading} onClick={() => handleLeer(row)}>Marcar leída</Button>
        : <span className="text-sm text-slate-400">Sin acción</span>
    }
  ]

  if (loading) return <Loader message="Cargando alertas de stock..." />

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Alertas de stock"
        title="Alertas de mi sucursal"
        description="Revisa productos que llegaron al stock mínimo o quedaron sin stock. Estas alertas se generan por movimientos de inventario."
      />

      {error && <Alert tone="error">{error}</Alert>}
      {success && <Alert tone="success">{success}</Alert>}

      <section className="grid gap-4 md:grid-cols-4">
        <Card title="Alertas" value={resumen.total} description="Según filtros" />
        <Card title="Pendientes" value={resumen.pendientes} description="Por revisar" />
        <Card title="Stock mínimo" value={resumen.minimo} description="Nivel bajo" />
        <Card title="Sin stock" value={resumen.agotado} description="Crítico" />
      </section>

      <Card>
        <div className="grid gap-3 md:grid-cols-2">
          <Input label="Buscar" placeholder="Producto, tipo o estado" value={search} onChange={(event) => setSearch(event.target.value)} />
          <Select label="Estado" value={estado} onChange={(event) => setEstado(event.target.value)}>
            <option value="PENDIENTE">Pendientes</option>
            <option value="LEIDA">Leídas</option>
          </Select>
        </div>
      </Card>

      <Table columns={columns} data={filtered} keyField="idAlerta" emptyMessage="No hay alertas con los filtros actuales." />
    </div>
  )
}
