import { useEffect, useMemo, useState } from 'react'
import { enviarReposicion, listarReposiciones } from '@/shared/api/reposicionApi'
import Alert from '@/shared/components/Alert'
import Badge from '@/shared/components/Badge'
import Button from '@/shared/components/Button'
import Card from '@/shared/components/Card'
import Input from '@/shared/components/Input'
import Loader from '@/shared/components/Loader'
import Modal from '@/shared/components/Modal'
import PageHeader from '@/shared/components/PageHeader'
import Select from '@/shared/components/Select'
import Table from '@/shared/components/Table'
import Textarea from '@/shared/components/Textarea'
import {
  ESTADOS_REPOSICION,
  formatDateTime,
  formatEstadoReposicion,
  getApiErrorMessage,
  getEstadoReposicionTone,
  totalDespachado,
  totalSolicitado
} from '@/shared/utils/reposiciones'

const estadoOptions = [
  { value: ESTADOS_REPOSICION.ACEPTADO, label: 'Aceptadas para despacho' },
  { value: ESTADOS_REPOSICION.EN_TRANSITO, label: 'En tránsito' },
  { value: ESTADOS_REPOSICION.RECIBIDA, label: 'Recibidas' },
  { value: '', label: 'Todos los despachos' }
]

export default function DespachosPage() {
  const [solicitudes, setSolicitudes] = useState([])
  const [estado, setEstado] = useState(ESTADOS_REPOSICION.ACEPTADO)
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [selectedSolicitud, setSelectedSolicitud] = useState(null)
  const [detailModalOpen, setDetailModalOpen] = useState(false)
  const [dispatchModalOpen, setDispatchModalOpen] = useState(false)
  const [observacion, setObservacion] = useState('')

  const filteredSolicitudes = useMemo(() => {
    const term = search.trim().toLowerCase()
    const despachos = solicitudes.filter((solicitud) => [
      ESTADOS_REPOSICION.ACEPTADO,
      ESTADOS_REPOSICION.EN_TRANSITO,
      ESTADOS_REPOSICION.RECIBIDA
    ].includes(solicitud.estado))

    if (!term) return despachos

    return despachos.filter((solicitud) => (
      String(solicitud.idSolicitud).includes(term) ||
      solicitud.ubicacionOrigen?.toLowerCase().includes(term) ||
      solicitud.ubicacionDestino?.toLowerCase().includes(term) ||
      solicitud.usuarioSolicitante?.toLowerCase().includes(term) ||
      solicitud.estado?.toLowerCase().includes(term) ||
      solicitud.detalles?.some((detalle) => detalle.nombreProducto?.toLowerCase().includes(term) || detalle.codigoBarras?.toLowerCase().includes(term))
    ))
  }, [solicitudes, search])

  const resumen = useMemo(() => ({
    aceptadas: filteredSolicitudes.filter((item) => item.estado === ESTADOS_REPOSICION.ACEPTADO).length,
    transito: filteredSolicitudes.filter((item) => item.estado === ESTADOS_REPOSICION.EN_TRANSITO).length,
    recibidas: filteredSolicitudes.filter((item) => item.estado === ESTADOS_REPOSICION.RECIBIDA).length,
    unidadesPendientes: filteredSolicitudes
      .filter((item) => item.estado === ESTADOS_REPOSICION.ACEPTADO)
      .reduce((sum, item) => sum + totalSolicitado(item), 0)
  }), [filteredSolicitudes])

  async function loadDespachos() {
    setError('')

    try {
      const data = await listarReposiciones({
        estado: estado || undefined,
        limite: 200
      })
      setSolicitudes(data)
    } catch (err) {
      setError(getApiErrorMessage(err, 'No se pudieron cargar los despachos'))
    }
  }

  useEffect(() => {
    let mounted = true

    async function initialLoad() {
      setLoading(true)
      try {
        await loadDespachos()
      } finally {
        if (mounted) setLoading(false)
      }
    }

    initialLoad()
    return () => { mounted = false }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    if (!loading) loadDespachos()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [estado])

  function openDetail(solicitud) {
    setSelectedSolicitud(solicitud)
    setDetailModalOpen(true)
  }

  function openDispatchModal(solicitud) {
    setError('')
    setSuccess('')
    setSelectedSolicitud(solicitud)
    setObservacion('')
    setDispatchModalOpen(true)
  }

  async function dispatchSolicitud() {
    if (!selectedSolicitud) return

    setActionLoading(true)
    setError('')

    try {
      await enviarReposicion(selectedSolicitud.idSolicitud, observacion)
      setSuccess('Despacho registrado. La solicitud pasó a EN_TRANSITO y el stock del almacén central fue descontado.')
      setDispatchModalOpen(false)
      setSelectedSolicitud(null)
      await loadDespachos()
    } catch (err) {
      setError(getApiErrorMessage(err, 'No se pudo registrar el despacho'))
    } finally {
      setActionLoading(false)
    }
  }

  const columns = [
    { key: 'idSolicitud', header: 'N°', render: (row) => <span className="font-black text-slate-950">#{row.idSolicitud}</span> },
    { key: 'destino', header: 'Sucursal destino', render: (row) => <div><p className="font-semibold text-slate-950">{row.ubicacionDestino}</p><p className="text-xs text-slate-500">Desde: {row.ubicacionOrigen}</p></div> },
    { key: 'estado', header: 'Estado', render: (row) => <Badge tone={getEstadoReposicionTone(row.estado)}>{formatEstadoReposicion(row.estado)}</Badge> },
    { key: 'cantidades', header: 'Cantidades', render: (row) => <span>{totalDespachado(row)} / {totalSolicitado(row)}</span> },
    { key: 'fechaSolicitud', header: 'Fecha solicitud', render: (row) => formatDateTime(row.fechaSolicitud) },
    { key: 'fechaDespacho', header: 'Fecha despacho', render: (row) => formatDateTime(row.fechaDespacho) },
    {
      key: 'acciones',
      header: 'Acciones',
      render: (row) => (
        <div className="flex flex-wrap gap-2">
          <Button type="button" variant="secondary" className="px-3 py-2" onClick={() => openDetail(row)}>Detalle</Button>
          {row.estado === ESTADOS_REPOSICION.ACEPTADO && (
            <Button type="button" className="px-3 py-2" disabled={actionLoading} onClick={() => openDispatchModal(row)}>Despachar</Button>
          )}
        </div>
      )
    }
  ]

  if (loading) return <Loader message="Cargando despachos..." />

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Reposiciones"
        title="Despachos a sucursales"
        description="Registra el envío de productos desde el almacén central hacia sucursales cuando una solicitud ya fue aceptada."
      />

      {error && <Alert tone="error">{error}</Alert>}
      {success && <Alert tone="success">{success}</Alert>}

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Card title="Aceptadas" value={resumen.aceptadas} description="Listas para despachar" />
        <Card title="En tránsito" value={resumen.transito} description="Pendientes de recepción" />
        <Card title="Recibidas" value={resumen.recibidas} description="Confirmadas por sucursal" />
        <Card title="Unidades pendientes" value={resumen.unidadesPendientes} description="Por despachar" />
      </section>

      <Card>
        <div className="grid gap-4 md:grid-cols-2">
          <Input label="Buscar despacho" placeholder="N°, sucursal, producto o estado" value={search} onChange={(event) => setSearch(event.target.value)} />
          <Select label="Estado" value={estado} onChange={(event) => setEstado(event.target.value)}>
            {estadoOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
          </Select>
        </div>
      </Card>

      <Table columns={columns} data={filteredSolicitudes} keyField="idSolicitud" emptyMessage="No hay solicitudes aceptadas o despachos para los filtros actuales." />

      <Modal
        isOpen={detailModalOpen}
        onClose={() => setDetailModalOpen(false)}
        title={selectedSolicitud ? `Solicitud #${selectedSolicitud.idSolicitud}` : 'Detalle de despacho'}
        description={selectedSolicitud ? `${selectedSolicitud.ubicacionOrigen} → ${selectedSolicitud.ubicacionDestino}` : ''}
        footer={<Button type="button" variant="secondary" onClick={() => setDetailModalOpen(false)}>Cerrar</Button>}
      >
        {selectedSolicitud && (
          <div className="space-y-5">
            <div className="grid gap-3 text-sm md:grid-cols-3">
              <div className="rounded-2xl bg-slate-50 p-4">
                <p className="text-slate-500">Estado</p>
                <div className="mt-2"><Badge tone={getEstadoReposicionTone(selectedSolicitud.estado)}>{formatEstadoReposicion(selectedSolicitud.estado)}</Badge></div>
              </div>
              <div className="rounded-2xl bg-slate-50 p-4">
                <p className="text-slate-500">Despachador</p>
                <p className="mt-2 font-semibold text-slate-950">{selectedSolicitud.usuarioDespachador || '-'}</p>
              </div>
              <div className="rounded-2xl bg-slate-50 p-4">
                <p className="text-slate-500">Receptor</p>
                <p className="mt-2 font-semibold text-slate-950">{selectedSolicitud.usuarioReceptor || '-'}</p>
              </div>
            </div>

            {selectedSolicitud.observacion && (
              <div className="rounded-2xl border border-slate-200 bg-white p-4 text-sm text-slate-600">
                <p className="font-semibold text-slate-950">Observación</p>
                <p className="mt-1 whitespace-pre-wrap">{selectedSolicitud.observacion}</p>
              </div>
            )}

            <Table
              columns={[
                { key: 'producto', header: 'Producto', render: (detalle) => <div><p className="font-semibold text-slate-900">{detalle.nombreProducto}</p><p className="text-xs text-slate-500">{detalle.codigoBarras}</p></div> },
                { key: 'cantidadSolicitada', header: 'Aprobada' },
                { key: 'cantidadDespachada', header: 'Despachada' }
              ]}
              data={selectedSolicitud.detalles || []}
              keyField="idDetalleSolicitud"
              emptyMessage="Esta solicitud no tiene detalle."
            />

            <div className="grid gap-3 rounded-2xl border border-slate-200 bg-white p-4 text-sm md:grid-cols-3">
              <div>
                <p className="text-slate-500">Fecha solicitud</p>
                <p className="font-bold text-slate-950">{formatDateTime(selectedSolicitud.fechaSolicitud)}</p>
              </div>
              <div>
                <p className="text-slate-500">Fecha despacho</p>
                <p className="font-bold text-slate-950">{formatDateTime(selectedSolicitud.fechaDespacho)}</p>
              </div>
              <div>
                <p className="text-slate-500">Fecha recepción</p>
                <p className="font-bold text-slate-950">{formatDateTime(selectedSolicitud.fechaRecepcion)}</p>
              </div>
            </div>
          </div>
        )}
      </Modal>

      <Modal
        isOpen={dispatchModalOpen}
        onClose={() => setDispatchModalOpen(false)}
        title="Registrar despacho"
        description={selectedSolicitud ? `Solicitud #${selectedSolicitud.idSolicitud}. Se descontará stock del almacén central y la solicitud pasará a EN_TRANSITO.` : ''}
        footer={(
          <>
            <Button type="button" variant="secondary" onClick={() => setDispatchModalOpen(false)}>Volver</Button>
            <Button type="button" disabled={actionLoading} onClick={dispatchSolicitud}>{actionLoading ? 'Procesando...' : 'Confirmar despacho'}</Button>
          </>
        )}
      >
        <Textarea
          label="Observación opcional"
          placeholder="Agrega un comentario para el despacho"
          value={observacion}
          onChange={(event) => setObservacion(event.target.value)}
          rows={4}
        />
      </Modal>
    </div>
  )
}
