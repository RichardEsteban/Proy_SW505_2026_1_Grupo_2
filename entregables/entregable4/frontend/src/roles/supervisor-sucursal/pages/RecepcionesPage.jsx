import { useEffect, useMemo, useState } from 'react'
import { listarReposiciones, recibirReposicion } from '@/shared/api/reposicionApi'
import { useAuth } from '@/shared/auth/AuthContext'
import Alert from '@/shared/components/Alert'
import Badge from '@/shared/components/Badge'
import Button from '@/shared/components/Button'
import Card from '@/shared/components/Card'
import Input from '@/shared/components/Input'
import Loader from '@/shared/components/Loader'
import Modal from '@/shared/components/Modal'
import PageHeader from '@/shared/components/PageHeader'
import Table from '@/shared/components/Table'
import Textarea from '@/shared/components/Textarea'
import { formatDateTime } from '@/shared/utils/roleViews'

function toneByEstado(estado) {
  if (estado === 'RECIBIDA') return 'green'
  if (estado === 'RECHAZADA' || estado === 'CANCELADA') return 'red'
  return 'amber'
}

export default function RecepcionesPage() {
  const { usuario } = useAuth()
  const [reposiciones, setReposiciones] = useState([])
  const [selected, setSelected] = useState(null)
  const [modalMode, setModalMode] = useState('detail')
  const [observacion, setObservacion] = useState('')
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  async function loadData() {
    setError('')
    try {
      const data = await listarReposiciones({ idUbicacionDestino: usuario?.idUbicacion, limite: 100 })
      setReposiciones(data)
    } catch (err) {
      setError(err.message || 'No se pudieron cargar las recepciones')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [usuario?.idUbicacion])

  const filtered = useMemo(() => {
    const term = search.trim().toLowerCase()
    return reposiciones.filter((item) => {
      const matchTerm = !term || [item.idSolicitud, item.estado, item.ubicacionOrigen, item.ubicacionDestino, item.observacion]
        .some((value) => String(value || '').toLowerCase().includes(term))
      return matchTerm
    })
  }, [reposiciones, search])

  const resumen = useMemo(() => ({
    total: reposiciones.length,
    porRecibir: reposiciones.filter((item) => item.estado === 'EN_TRANSITO').length,
    recibidas: reposiciones.filter((item) => item.estado === 'RECIBIDA').length,
    incidencias: reposiciones.filter((item) => String(item.observacion || '').toLowerCase().includes('incidencia')).length
  }), [reposiciones])

  function openDetalle(row) {
    setSelected(row)
    setModalMode('detail')
    setObservacion('')
    setError('')
    setSuccess('')
  }

  function openRecepcion(row) {
    setSelected(row)
    setModalMode('receive')
    setObservacion('')
    setError('')
    setSuccess('')
  }

  async function handleRecibir(event) {
    event.preventDefault()
    if (!selected) return
    setActionLoading(true)
    setError('')
    setSuccess('')
    try {
      await recibirReposicion(selected.idSolicitud, observacion)
      setSuccess('Recepción confirmada correctamente')
      setSelected(null)
      await loadData()
    } catch (err) {
      setError(err.message || 'No se pudo confirmar la recepción')
    } finally {
      setActionLoading(false)
    }
  }

  const columns = [
    { key: 'idSolicitud', header: 'Pedido', render: (row) => <span className="font-semibold text-slate-950">TRANS-{String(row.idSolicitud).padStart(4, '0')}</span> },
    { key: 'fechaSolicitud', header: 'Fecha', render: (row) => formatDateTime(row.fechaSolicitud) },
    { key: 'ubicacionOrigen', header: 'Origen', render: (row) => row.ubicacionOrigen || row.origen || '-' },
    { key: 'estado', header: 'Estado', render: (row) => <Badge tone={toneByEstado(row.estado)}>{row.estado}</Badge> },
    { key: 'observacion', header: 'Observación', render: (row) => row.observacion || '-' },
    { key: 'acciones', header: 'Acciones', render: (row) => (
      <div className="flex flex-wrap justify-end gap-2">
        <Button type="button" variant="secondary" className="px-3 py-2" onClick={() => openDetalle(row)}>Ver</Button>
        {row.estado === 'EN_TRANSITO'
          ? <Button type="button" className="px-3 py-2" onClick={() => openRecepcion(row)}>Confirmar recepción</Button>
          : <span className="text-sm text-slate-400">Solo consulta</span>}
      </div>
    ) }
  ]

  if (loading) return <Loader message="Cargando recepciones..." />

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Recepciones"
        title="Recepción de mercadería"
        description="Confirma mercadería enviada por almacén central y registra incidencias en la observación si se presentaron."
      />

      {error && <Alert tone="error">{error}</Alert>}
      {success && <Alert tone="success">{success}</Alert>}

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Card title="Total pedidos" value={resumen.total} description="Asignados a tu sucursal" />
        <Card title="Por recibir" value={resumen.porRecibir} description="En tránsito" />
        <Card title="Recibidas" value={resumen.recibidas} description="Confirmadas" />
        <Card title="Incidencias" value={resumen.incidencias} description="Detectadas por texto" />
      </section>

      <Card>
        <Input label="Buscar recepción" placeholder="Número, estado, origen u observación" value={search} onChange={(event) => setSearch(event.target.value)} />
      </Card>

      <Table columns={columns} data={filtered} keyField="idSolicitud" emptyMessage="No hay recepciones con los filtros actuales." />

      <Modal
        isOpen={Boolean(selected)}
        onClose={() => setSelected(null)}
        title={modalMode === 'receive' ? 'Confirmar recepción' : 'Detalle de recepción'}
        description={selected ? `Pedido TRANS-${String(selected.idSolicitud).padStart(4, '0')}` : ''}
        footer={modalMode === 'receive' ? (
          <>
            <Button type="button" variant="secondary" onClick={() => setSelected(null)}>Cancelar</Button>
            <Button type="submit" form="recepcion-form" disabled={actionLoading}>{actionLoading ? 'Confirmando...' : 'Confirmar recepción'}</Button>
          </>
        ) : <Button type="button" variant="secondary" onClick={() => setSelected(null)}>Cerrar</Button>}
      >
        {selected && (
          <div className="space-y-4">
            <div className="grid gap-3 text-sm md:grid-cols-3">
              <div className="rounded-2xl bg-slate-50 p-4"><p className="text-slate-500">Origen</p><p className="mt-1 font-semibold text-slate-950">{selected.ubicacionOrigen || '-'}</p></div>
              <div className="rounded-2xl bg-slate-50 p-4"><p className="text-slate-500">Estado</p><div className="mt-1"><Badge tone={toneByEstado(selected.estado)}>{selected.estado}</Badge></div></div>
              <div className="rounded-2xl bg-slate-50 p-4"><p className="text-slate-500">Fecha</p><p className="mt-1 font-semibold text-slate-950">{formatDateTime(selected.fechaSolicitud)}</p></div>
            </div>

            <Table
              columns={[
                { key: 'producto', header: 'Producto', render: (detalle) => <div><p className="font-semibold text-slate-900">{detalle.nombreProducto}</p><p className="text-xs text-slate-500">{detalle.codigoBarras}</p></div> },
                { key: 'cantidadSolicitada', header: 'Solicitada' },
                { key: 'cantidadDespachada', header: 'Despachada' }
              ]}
              data={selected.detalles || []}
              keyField="idDetalleSolicitud"
              emptyMessage="Esta recepción no tiene detalle."
            />

            {modalMode === 'receive' && (
              <form id="recepcion-form" className="space-y-4" onSubmit={handleRecibir}>
                <Textarea
                  label="Observación / incidencia"
                  placeholder="Ejemplo: Mercadería completa. O: Incidencia: faltaron 2 unidades del producto X."
                  value={observacion}
                  onChange={(event) => setObservacion(event.target.value)}
                />
              </form>
            )}
          </div>
        )}
      </Modal>
    </div>
  )
}
