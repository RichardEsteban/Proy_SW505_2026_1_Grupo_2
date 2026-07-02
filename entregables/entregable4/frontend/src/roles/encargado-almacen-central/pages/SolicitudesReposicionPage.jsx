import { useEffect, useMemo, useState } from 'react'
import {
  abrirRevisionReposicion,
  aprobarReposicion,
  listarReposiciones,
  rechazarReposicion
} from '@/shared/api/reposicionApi'
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
  summarizeReposiciones,
  totalDespachado,
  totalSolicitado
} from '@/shared/utils/reposiciones'

const estadoOptions = [
  { value: '', label: 'Todas las solicitudes' },
  { value: ESTADOS_REPOSICION.ENVIADO, label: 'Enviadas' },
  { value: ESTADOS_REPOSICION.EN_REVISION, label: 'En revisión' },
  { value: ESTADOS_REPOSICION.ACEPTADO, label: 'Aceptadas' },
  { value: ESTADOS_REPOSICION.RECHAZADA, label: 'Rechazadas' },
  { value: ESTADOS_REPOSICION.CANCELADA, label: 'Canceladas' }
]

const actionLabels = {
  abrirRevision: {
    title: 'Tomar en revisión',
    description: 'La solicitud pasará de ENVIADO a EN_REVISION y quedará bloqueada para evaluación.',
    confirm: 'Tomar en revisión',
    success: 'Solicitud tomada en revisión.'
  },
  aprobar: {
    title: 'Aprobar solicitud',
    description: 'La solicitud quedará ACEPTADA y lista para despacho.',
    confirm: 'Aprobar',
    success: 'Solicitud aprobada correctamente.'
  },
  rechazar: {
    title: 'Rechazar solicitud',
    description: 'Debes ingresar el motivo del rechazo.',
    confirm: 'Rechazar',
    success: 'Solicitud rechazada correctamente.'
  }
}

export default function SolicitudesReposicionPage() {
  const [solicitudes, setSolicitudes] = useState([])
  const [estado, setEstado] = useState('')
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [selectedSolicitud, setSelectedSolicitud] = useState(null)
  const [detailModalOpen, setDetailModalOpen] = useState(false)
  const [actionModalOpen, setActionModalOpen] = useState(false)
  const [actionType, setActionType] = useState('')
  const [actionObservation, setActionObservation] = useState('')

  const filteredSolicitudes = useMemo(() => {
    const term = search.trim().toLowerCase()
    if (!term) return solicitudes

    return solicitudes.filter((solicitud) => (
      String(solicitud.idSolicitud).includes(term) ||
      solicitud.ubicacionOrigen?.toLowerCase().includes(term) ||
      solicitud.ubicacionDestino?.toLowerCase().includes(term) ||
      solicitud.usuarioSolicitante?.toLowerCase().includes(term) ||
      solicitud.estado?.toLowerCase().includes(term) ||
      solicitud.detalles?.some((detalle) => detalle.nombreProducto?.toLowerCase().includes(term) || detalle.codigoBarras?.toLowerCase().includes(term))
    ))
  }, [solicitudes, search])

  const resumen = useMemo(() => summarizeReposiciones(filteredSolicitudes), [filteredSolicitudes])

  async function loadSolicitudes() {
    setError('')

    try {
      const data = await listarReposiciones({
        estado: estado || undefined,
        limite: 200
      })
      setSolicitudes(data)
    } catch (err) {
      setError(getApiErrorMessage(err, 'No se pudieron cargar las solicitudes de reposición'))
    }
  }

  useEffect(() => {
    let mounted = true

    async function initialLoad() {
      setLoading(true)
      try {
        await loadSolicitudes()
      } finally {
        if (mounted) setLoading(false)
      }
    }

    initialLoad()
    return () => { mounted = false }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    if (!loading) loadSolicitudes()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [estado])

  function openDetail(solicitud) {
    setSelectedSolicitud(solicitud)
    setDetailModalOpen(true)
  }

  function openActionModal(solicitud, type) {
    setError('')
    setSuccess('')
    setSelectedSolicitud(solicitud)
    setActionType(type)
    setActionObservation('')
    setActionModalOpen(true)
  }

  async function runAction() {
    if (!selectedSolicitud || !actionType) return

    if (actionType === 'rechazar' && !actionObservation.trim()) {
      setError('Debes ingresar el motivo del rechazo.')
      return
    }

    const actions = {
      abrirRevision: abrirRevisionReposicion,
      aprobar: aprobarReposicion,
      rechazar: rechazarReposicion
    }

    setActionLoading(true)
    setError('')

    try {
      await actions[actionType](selectedSolicitud.idSolicitud, actionObservation)
      setSuccess(actionLabels[actionType].success)
      setActionModalOpen(false)
      setSelectedSolicitud(null)
      await loadSolicitudes()
    } catch (err) {
      setError(getApiErrorMessage(err, 'No se pudo actualizar la solicitud'))
    } finally {
      setActionLoading(false)
    }
  }

  const columns = [
    { key: 'idSolicitud', header: 'N°', render: (row) => <span className="font-black text-slate-950">#{row.idSolicitud}</span> },
    { key: 'sucursal', header: 'Sucursal solicitante', render: (row) => <div><p className="font-semibold text-slate-950">{row.ubicacionDestino}</p><p className="text-xs text-slate-500">Origen: {row.ubicacionOrigen}</p></div> },
    { key: 'estado', header: 'Estado', render: (row) => <Badge tone={getEstadoReposicionTone(row.estado)}>{formatEstadoReposicion(row.estado)}</Badge> },
    { key: 'cantidades', header: 'Cantidades', render: (row) => <span>{totalDespachado(row)} / {totalSolicitado(row)}</span> },
    { key: 'fechaSolicitud', header: 'Fecha', render: (row) => formatDateTime(row.fechaSolicitud) },
    {
      key: 'acciones',
      header: 'Acciones',
      render: (row) => (
        <div className="flex flex-wrap gap-2">
          <Button type="button" variant="secondary" className="px-3 py-2" onClick={() => openDetail(row)}>Detalle</Button>
          {row.estado === ESTADOS_REPOSICION.ENVIADO && (
            <Button type="button" variant="secondary" className="px-3 py-2" disabled={actionLoading} onClick={() => openActionModal(row, 'abrirRevision')}>Revisión</Button>
          )}
          {[ESTADOS_REPOSICION.ENVIADO, ESTADOS_REPOSICION.EN_REVISION].includes(row.estado) && (
            <>
              <Button type="button" className="px-3 py-2" disabled={actionLoading} onClick={() => openActionModal(row, 'aprobar')}>Aprobar</Button>
              <Button type="button" variant="danger" className="px-3 py-2" disabled={actionLoading} onClick={() => openActionModal(row, 'rechazar')}>Rechazar</Button>
            </>
          )}
        </div>
      )
    }
  ]

  const actionConfig = actionLabels[actionType]

  if (loading) return <Loader message="Cargando solicitudes de reposición..." />

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Reposiciones"
        title="Solicitudes de reposición"
        description="Revisa las solicitudes enviadas por sucursales, tómalas en revisión y apruébalas o recházalas según disponibilidad."
      />

      {error && <Alert tone="error">{error}</Alert>}
      {success && <Alert tone="success">{success}</Alert>}

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        <Card title="Solicitudes" value={resumen.total} description="Según filtros aplicados" />
        <Card title="Pendientes" value={resumen.pendientes} description="Enviadas o en revisión" />
        <Card title="Aceptadas" value={resumen.aceptadas} description="Listas para despacho" />
        <Card title="Rechazadas" value={filteredSolicitudes.filter((item) => item.estado === ESTADOS_REPOSICION.RECHAZADA).length} description="No aprobadas" />
        <Card title="Canceladas" value={filteredSolicitudes.filter((item) => item.estado === ESTADOS_REPOSICION.CANCELADA).length} description="Sin atención" />
      </section>

      <Card>
        <div className="grid gap-4 md:grid-cols-2">
          <Input label="Buscar solicitud" placeholder="N°, sucursal, producto o estado" value={search} onChange={(event) => setSearch(event.target.value)} />
          <Select label="Estado" value={estado} onChange={(event) => setEstado(event.target.value)}>
            {estadoOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
          </Select>
        </div>
      </Card>

      <Table columns={columns} data={filteredSolicitudes} keyField="idSolicitud" emptyMessage="No hay solicitudes de reposición para los filtros actuales." />

      <Modal
        isOpen={detailModalOpen}
        onClose={() => setDetailModalOpen(false)}
        title={selectedSolicitud ? `Solicitud #${selectedSolicitud.idSolicitud}` : 'Detalle de solicitud'}
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
                <p className="text-slate-500">Solicitante</p>
                <p className="mt-2 font-semibold text-slate-950">{selectedSolicitud.usuarioSolicitante}</p>
              </div>
              <div className="rounded-2xl bg-slate-50 p-4">
                <p className="text-slate-500">Fecha solicitud</p>
                <p className="mt-2 font-semibold text-slate-950">{formatDateTime(selectedSolicitud.fechaSolicitud)}</p>
              </div>
            </div>

            {selectedSolicitud.observacion && (
              <div className="rounded-2xl border border-slate-200 bg-white p-4 text-sm text-slate-600">
                <p className="font-semibold text-slate-950">Observación / motivo</p>
                <p className="mt-1 whitespace-pre-wrap">{selectedSolicitud.observacion}</p>
              </div>
            )}

            <Table
              columns={[
                { key: 'producto', header: 'Producto', render: (detalle) => <div><p className="font-semibold text-slate-900">{detalle.nombreProducto}</p><p className="text-xs text-slate-500">{detalle.codigoBarras}</p></div> },
                { key: 'cantidadSolicitada', header: 'Solicitada' },
                { key: 'cantidadDespachada', header: 'Despachada' }
              ]}
              data={selectedSolicitud.detalles || []}
              keyField="idDetalleSolicitud"
              emptyMessage="Esta solicitud no tiene detalle."
            />
          </div>
        )}
      </Modal>

      <Modal
        isOpen={actionModalOpen}
        onClose={() => setActionModalOpen(false)}
        title={actionConfig?.title || 'Gestionar solicitud'}
        description={selectedSolicitud ? `Solicitud #${selectedSolicitud.idSolicitud}. ${actionConfig?.description || ''}` : actionConfig?.description}
        footer={(
          <>
            <Button type="button" variant="secondary" onClick={() => setActionModalOpen(false)}>Volver</Button>
            <Button type="button" variant={actionType === 'rechazar' ? 'danger' : 'primary'} disabled={actionLoading} onClick={runAction}>
              {actionLoading ? 'Procesando...' : actionConfig?.confirm || 'Confirmar'}
            </Button>
          </>
        )}
      >
        <Textarea
          label={actionType === 'rechazar' ? 'Motivo del rechazo' : 'Observación opcional'}
          placeholder={actionType === 'rechazar' ? 'Explica por qué se rechaza la solicitud' : 'Agrega un comentario para esta gestión'}
          value={actionObservation}
          onChange={(event) => setActionObservation(event.target.value)}
          rows={4}
        />
      </Modal>
    </div>
  )
}
