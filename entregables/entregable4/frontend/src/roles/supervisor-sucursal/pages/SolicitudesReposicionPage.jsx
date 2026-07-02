import { useEffect, useMemo, useState } from 'react'
import { cancelarReposicion, crearReposicion, editarReposicion, listarReposiciones } from '@/shared/api/reposicionApi'
import { listarInventario } from '@/shared/api/inventarioApi'
import { useAuth } from '@/shared/auth/AuthContext'
import Alert from '@/shared/components/Alert'
import Badge from '@/shared/components/Badge'
import Button from '@/shared/components/Button'
import Card from '@/shared/components/Card'
import Input from '@/shared/components/Input'
import Loader from '@/shared/components/Loader'
import Modal from '@/shared/components/Modal'
import PageHeader from '@/shared/components/PageHeader'
import ProductPicker from '@/shared/components/ProductPicker'
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
  toIsoFromLocalDateTime,
  totalDespachado,
  totalSolicitado
} from '@/shared/utils/reposiciones'

const emptyForm = {
  observacion: '',
  detalles: []
}

const estadoOptions = [
  { value: '', label: 'Todos los estados' },
  { value: ESTADOS_REPOSICION.ENVIADO, label: 'Enviado' },
  { value: ESTADOS_REPOSICION.EN_REVISION, label: 'En revisión' },
  { value: ESTADOS_REPOSICION.ACEPTADO, label: 'Aceptado' },
  { value: ESTADOS_REPOSICION.EN_TRANSITO, label: 'En tránsito' },
  { value: ESTADOS_REPOSICION.RECIBIDA, label: 'Recibida' },
  { value: ESTADOS_REPOSICION.RECHAZADA, label: 'Rechazada' },
  { value: ESTADOS_REPOSICION.CANCELADA, label: 'Cancelada' }
]

function canEditRequest(solicitud) {
  return solicitud.estado === ESTADOS_REPOSICION.ENVIADO
}

function canCancelRequest(solicitud) {
  return solicitud.estado === ESTADOS_REPOSICION.ENVIADO
}

export default function SolicitudesReposicionPage() {
  const { usuario } = useAuth()
  const [reposiciones, setReposiciones] = useState([])
  const [inventario, setInventario] = useState([])
  const [estado, setEstado] = useState('')
  const [desde, setDesde] = useState('')
  const [hasta, setHasta] = useState('')
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [formModalOpen, setFormModalOpen] = useState(false)
  const [detailModalOpen, setDetailModalOpen] = useState(false)
  const [cancelModalOpen, setCancelModalOpen] = useState(false)
  const [selected, setSelected] = useState(null)
  const [formMode, setFormMode] = useState('create')
  const [form, setForm] = useState(emptyForm)
  const [cancelObservation, setCancelObservation] = useState('')

  const productosDisponibles = useMemo(() => inventario.filter((item) => item.idProducto && item.producto), [inventario])

  async function loadData() {
    setError('')
    try {
      const idUbicacion = usuario?.idUbicacion
      const [reposicionesData, inventarioData] = await Promise.all([
        listarReposiciones({
          idUbicacionDestino: idUbicacion,
          estado: estado || undefined,
          desde: toIsoFromLocalDateTime(desde),
          hasta: toIsoFromLocalDateTime(hasta),
          limite: 200
        }),
        listarInventario({ idUbicacion })
      ])
      setReposiciones(reposicionesData)
      setInventario(inventarioData)
    } catch (err) {
      setError(getApiErrorMessage(err, 'No se pudieron cargar las solicitudes de reposición'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [usuario?.idUbicacion, estado, desde, hasta])

  const filtered = useMemo(() => {
    const term = search.trim().toLowerCase()
    if (!term) return reposiciones
    return reposiciones.filter((solicitud) => (
      String(solicitud.idSolicitud).includes(term) ||
      solicitud.ubicacionOrigen?.toLowerCase().includes(term) ||
      solicitud.estado?.toLowerCase().includes(term) ||
      solicitud.observacion?.toLowerCase().includes(term) ||
      solicitud.detalles?.some((detalle) => detalle.nombreProducto?.toLowerCase().includes(term) || detalle.codigoBarras?.toLowerCase().includes(term))
    ))
  }, [reposiciones, search])

  const resumen = useMemo(() => summarizeReposiciones(filtered), [filtered])

  function resetMessages() {
    setError('')
    setSuccess('')
  }

  function openCreateModal() {
    resetMessages()
    setSelected(null)
    setFormMode('create')
    setForm(emptyForm)
    setFormModalOpen(true)
  }

  function openEditModal(solicitud) {
    resetMessages()
    setSelected(solicitud)
    setFormMode('edit')
    setForm({
      observacion: solicitud.observacion || '',
      detalles: (solicitud.detalles || []).map((detalle) => ({
        idProducto: String(detalle.idProducto),
        cantidadSolicitada: detalle.cantidadSolicitada
      }))
    })
    setFormModalOpen(true)
  }

  function openDetail(solicitud) {
    setSelected(solicitud)
    setDetailModalOpen(true)
  }

  function openCancelModal(solicitud) {
    resetMessages()
    setSelected(solicitud)
    setCancelObservation('')
    setCancelModalOpen(true)
  }
  function validateForm() {
    if (!form.detalles.length) return 'Agrega al menos un producto.'
    for (const detalle of form.detalles) {
      if (!detalle.idProducto) return 'Selecciona un producto en cada línea.'
      if (Number(detalle.cantidadSolicitada) <= 0) return 'La cantidad solicitada debe ser mayor que cero.'
    }
    return ''
  }

  async function handleSubmit(event) {
    event.preventDefault()
    resetMessages()

    const validationError = validateForm()
    if (validationError) {
      setError(validationError)
      return
    }

    const payload = {
      observacion: form.observacion?.trim() || null,
      detalles: form.detalles.map((detalle) => ({
        idProducto: Number(detalle.idProducto),
        cantidadSolicitada: Number(detalle.cantidadSolicitada)
      }))
    }

    setActionLoading(true)
    try {
      if (formMode === 'edit' && selected) {
        await editarReposicion(selected.idSolicitud, payload)
        setSuccess('Solicitud actualizada correctamente.')
      } else {
        await crearReposicion(payload)
        setSuccess('Solicitud enviada correctamente al almacén central.')
      }
      setFormModalOpen(false)
      setSelected(null)
      await loadData()
    } catch (err) {
      setError(getApiErrorMessage(err, 'No se pudo guardar la solicitud'))
    } finally {
      setActionLoading(false)
    }
  }

  async function handleCancelRequest() {
    if (!selected) return
    setActionLoading(true)
    resetMessages()
    try {
      await cancelarReposicion(selected.idSolicitud, cancelObservation)
      setSuccess('Solicitud cancelada correctamente.')
      setCancelModalOpen(false)
      setSelected(null)
      setCancelObservation('')
      await loadData()
    } catch (err) {
      setError(getApiErrorMessage(err, 'No se pudo cancelar la solicitud'))
    } finally {
      setActionLoading(false)
    }
  }

  const columns = [
    { key: 'idSolicitud', header: 'Solicitud', render: (row) => <span className="font-semibold text-slate-950">SOL-{String(row.idSolicitud).padStart(4, '0')}</span> },
    { key: 'fechaSolicitud', header: 'Fecha', render: (row) => formatDateTime(row.fechaSolicitud) },
    { key: 'origen', header: 'Origen', render: (row) => row.ubicacionOrigen || 'Almacén central' },
    { key: 'cantidades', header: 'Cantidad', render: (row) => <div><p>Solicitada: <span className="font-bold text-slate-950">{totalSolicitado(row)}</span></p><p className="text-xs text-slate-500">Despachada: {totalDespachado(row)}</p></div> },
    { key: 'estado', header: 'Estado', render: (row) => <Badge tone={getEstadoReposicionTone(row.estado)}>{formatEstadoReposicion(row.estado)}</Badge> },
    {
      key: 'acciones',
      header: 'Acciones',
      className: 'text-right',
      render: (row) => (
        <div className="flex flex-wrap justify-end gap-2">
          <Button type="button" variant="secondary" className="px-3 py-2" onClick={() => openDetail(row)}>Ver</Button>
          {canEditRequest(row) && <Button type="button" variant="secondary" className="px-3 py-2" onClick={() => openEditModal(row)}>Editar</Button>}
          {canCancelRequest(row) && <Button type="button" variant="danger" className="px-3 py-2" onClick={() => openCancelModal(row)}>Cancelar</Button>}
          {!canEditRequest(row) && !canCancelRequest(row) && <span className="text-sm text-slate-400">Solo consulta</span>}
        </div>
      )
    }
  ]

  if (loading) return <Loader message="Cargando solicitudes de reposición..." />

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Solicitudes de reposición"
        title="Solicitudes de mi sucursal"
        description="Crea solicitudes hacia el almacén central y consulta, edita o cancela solicitudes mientras sigan en estado Enviado."
        action={<Button type="button" onClick={openCreateModal}>Nueva solicitud</Button>}
      />

      {error && <Alert tone="error">{error}</Alert>}
      {success && <Alert tone="success">{success}</Alert>}

      <section className="grid gap-4 md:grid-cols-5">
        <Card title="Solicitudes" value={resumen.total} description="Según filtros" />
        <Card title="Pendientes" value={resumen.pendientes} description="Enviado / revisión" />
        <Card title="Aceptadas" value={resumen.aceptadas} description="Listas para despacho" />
        <Card title="En tránsito" value={resumen.transito} description="Por recibir" />
        <Card title="Recibidas" value={resumen.recibidas} description="Finalizadas" />
      </section>

      <Card>
        <div className="grid gap-3 lg:grid-cols-5">
          <Input label="Buscar" placeholder="ID, producto, estado u observación" value={search} onChange={(event) => setSearch(event.target.value)} />
          <Select label="Estado" value={estado} onChange={(event) => setEstado(event.target.value)}>
            {estadoOptions.map((option) => <option key={option.value || 'todos'} value={option.value}>{option.label}</option>)}
          </Select>
          <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3">
            <p className="text-xs font-bold uppercase tracking-wide text-slate-500">Mi sucursal</p>
            <p className="mt-1 text-sm font-semibold text-slate-950">{usuario?.ubicacion || 'Sucursal asignada'}</p>
          </div>
          <Input label="Desde" type="datetime-local" value={desde} onChange={(event) => setDesde(event.target.value)} />
          <Input label="Hasta" type="datetime-local" value={hasta} onChange={(event) => setHasta(event.target.value)} />
        </div>
      </Card>

      <Table columns={columns} data={filtered} keyField="idSolicitud" emptyMessage="No hay solicitudes de reposición para mostrar." />

      <Modal
        isOpen={formModalOpen}
        onClose={() => setFormModalOpen(false)}
        size="xl"
        title={formMode === 'edit' ? 'Editar solicitud' : 'Nueva solicitud de reposición'}
        description="El origen es el almacén central y el destino es tu sucursal asignada. El stock no cambia hasta que almacén despache y tu sucursal reciba."
        footer={(
          <>
            <Button type="button" variant="secondary" onClick={() => setFormModalOpen(false)}>Cancelar</Button>
            <Button type="submit" form="solicitud-reposicion-form" disabled={actionLoading}>{actionLoading ? 'Guardando...' : formMode === 'edit' ? 'Guardar cambios' : 'Enviar solicitud'}</Button>
          </>
        )}
      >
        <form id="solicitud-reposicion-form" className="space-y-5" onSubmit={handleSubmit}>
          <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
            <p><span className="font-semibold text-slate-950">Origen:</span> Almacén Central</p>
            <p><span className="font-semibold text-slate-950">Destino:</span> {usuario?.ubicacion || 'tu sucursal'}</p>
            <p className="mt-2 text-xs text-slate-500">Solo se pueden editar o cancelar solicitudes mientras estén en estado Enviado y dentro del tiempo permitido por la empresa.</p>
          </div>

          <Textarea
            label="Observación"
            placeholder="Ejemplo: stock bajo para fin de semana"
            value={form.observacion}
            onChange={(event) => setForm((current) => ({ ...current, observacion: event.target.value }))}
            rows={3}
          />

          <ProductPicker
            title="Buscar productos para reposición"
            description="Busca por nombre o código, filtra por categoría y prioriza los productos con menor stock."
            products={productosDisponibles}
            selectedItems={form.detalles}
            onChange={(detalles) => setForm((current) => ({ ...current, detalles }))}
            quantityField="cantidadSolicitada"
            quantityLabel="Cantidad solicitada"
            selectedTitle="Productos solicitados"
            addButtonLabel="Agregar"
            showStock
            showStockMin
            lowStockFirst
            selectedEmptyMessage="Agrega al menos un producto a la solicitud."
          />
        </form>
      </Modal>

      <Modal
        isOpen={detailModalOpen}
        onClose={() => setDetailModalOpen(false)}
        title={selected ? `Solicitud SOL-${String(selected.idSolicitud).padStart(4, '0')}` : 'Detalle de solicitud'}
        description={selected ? `${selected.ubicacionOrigen} → ${selected.ubicacionDestino}` : ''}
        footer={<Button type="button" variant="secondary" onClick={() => setDetailModalOpen(false)}>Cerrar</Button>}
      >
        {selected && (
          <div className="space-y-5">
            <div className="grid gap-3 text-sm md:grid-cols-3">
              <div className="rounded-2xl bg-slate-50 p-4">
                <p className="text-slate-500">Estado</p>
                <div className="mt-2"><Badge tone={getEstadoReposicionTone(selected.estado)}>{formatEstadoReposicion(selected.estado)}</Badge></div>
              </div>
              <div className="rounded-2xl bg-slate-50 p-4">
                <p className="text-slate-500">Solicitante</p>
                <p className="mt-2 font-semibold text-slate-950">{selected.usuarioSolicitante}</p>
              </div>
              <div className="rounded-2xl bg-slate-50 p-4">
                <p className="text-slate-500">Responsables</p>
                <p className="mt-2 font-semibold text-slate-950">{selected.usuarioDespachador || '-'} / {selected.usuarioReceptor || '-'}</p>
              </div>
            </div>

            {selected.observacion && (
              <div className="rounded-2xl border border-slate-200 bg-white p-4 text-sm text-slate-600">
                <p className="font-semibold text-slate-950">Observación</p>
                <p className="mt-1 whitespace-pre-wrap">{selected.observacion}</p>
              </div>
            )}

            <Table
              columns={[
                { key: 'producto', header: 'Producto', render: (detalle) => <div><p className="font-semibold text-slate-900">{detalle.nombreProducto}</p><p className="text-xs text-slate-500">{detalle.codigoBarras}</p></div> },
                { key: 'cantidadSolicitada', header: 'Solicitada' },
                { key: 'cantidadDespachada', header: 'Despachada' }
              ]}
              data={selected.detalles || []}
              keyField="idDetalleSolicitud"
              emptyMessage="Esta solicitud no tiene detalle."
            />

            <div className="grid gap-3 rounded-2xl border border-slate-200 bg-white p-4 text-sm md:grid-cols-3">
              <div><p className="text-slate-500">Fecha solicitud</p><p className="font-bold text-slate-950">{formatDateTime(selected.fechaSolicitud)}</p></div>
              <div><p className="text-slate-500">Fecha despacho</p><p className="font-bold text-slate-950">{formatDateTime(selected.fechaDespacho)}</p></div>
              <div><p className="text-slate-500">Fecha recepción</p><p className="font-bold text-slate-950">{formatDateTime(selected.fechaRecepcion)}</p></div>
            </div>
          </div>
        )}
      </Modal>

      <Modal
        isOpen={cancelModalOpen}
        onClose={() => setCancelModalOpen(false)}
        title="Cancelar solicitud"
        description={selected ? `Solicitud SOL-${String(selected.idSolicitud).padStart(4, '0')}. Solo se permite cancelar mientras está en estado Enviado.` : ''}
        footer={(
          <>
            <Button type="button" variant="secondary" onClick={() => setCancelModalOpen(false)}>Volver</Button>
            <Button type="button" variant="danger" disabled={actionLoading} onClick={handleCancelRequest}>{actionLoading ? 'Cancelando...' : 'Cancelar solicitud'}</Button>
          </>
        )}
      >
        <Textarea
          label="Motivo de cancelación"
          placeholder="Ejemplo: se corrigió el stock o ya no es necesario el pedido"
          value={cancelObservation}
          onChange={(event) => setCancelObservation(event.target.value)}
          rows={4}
        />
      </Modal>
    </div>
  )
}
