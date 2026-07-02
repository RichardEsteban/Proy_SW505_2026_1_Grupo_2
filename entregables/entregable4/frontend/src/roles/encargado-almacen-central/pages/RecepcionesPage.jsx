import { useEffect, useMemo, useState } from 'react'
import { listarOrdenesCompra, recibirOrdenCompra } from '@/shared/api/ordenCompraApi'
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
import { formatMoney } from '@/shared/utils/formatMoney'
import {
  ESTADOS_COMPRA,
  formatDateTime,
  formatEstadoCompra,
  getApiErrorMessage,
  getEstadoCompraTone,
  moneyNumber,
  roundMoney
} from '@/shared/utils/compras'

const estadoOptions = [
  { value: '', label: 'Todas' },
  { value: ESTADOS_COMPRA.SOLICITADO, label: 'Pendientes de recepción' },
  { value: ESTADOS_COMPRA.EN_TRANSITO, label: 'En tránsito' },
  { value: ESTADOS_COMPRA.RECIBIDO, label: 'Recibidas' },
  { value: ESTADOS_COMPRA.CANCELADO, label: 'Canceladas' }
]

export default function RecepcionesPage() {
  const [ordenes, setOrdenes] = useState([])
  const [estado, setEstado] = useState(ESTADOS_COMPRA.SOLICITADO)
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [selectedOrden, setSelectedOrden] = useState(null)

  async function loadOrdenes() {
    setError('')

    try {
      const data = await listarOrdenesCompra({
        estado: estado || undefined,
        limite: 200
      })
      setOrdenes(data)
    } catch (err) {
      setError(getApiErrorMessage(err, 'No se pudieron cargar las órdenes pendientes de recepción'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadOrdenes()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [estado])

  const filteredOrdenes = useMemo(() => {
    const term = search.trim().toLowerCase()
    if (!term) return ordenes

    return ordenes.filter((orden) => (
      String(orden.idOrdenCompra).includes(term) ||
      String(orden.proveedor || '').toLowerCase().includes(term) ||
      String(orden.ubicacionDestino || '').toLowerCase().includes(term) ||
      String(orden.usuarioComprador || '').toLowerCase().includes(term) ||
      String(orden.estado || '').toLowerCase().includes(term)
    ))
  }, [ordenes, search])

  const resumen = useMemo(() => ({
    total: filteredOrdenes.length,
    pendientes: filteredOrdenes.filter((orden) => [ESTADOS_COMPRA.SOLICITADO, ESTADOS_COMPRA.EN_TRANSITO].includes(orden.estado)).length,
    recibidas: filteredOrdenes.filter((orden) => orden.estado === ESTADOS_COMPRA.RECIBIDO).length,
    montoPendiente: roundMoney(filteredOrdenes
      .filter((orden) => [ESTADOS_COMPRA.SOLICITADO, ESTADOS_COMPRA.EN_TRANSITO].includes(orden.estado))
      .reduce((sum, orden) => sum + moneyNumber(orden.totalCompra), 0))
  }), [filteredOrdenes])

  function openDetalle(orden) {
    setSelectedOrden(orden)
    setError('')
    setSuccess('')
  }

  async function handleRecibir() {
    if (!selectedOrden) return

    setActionLoading(true)
    setError('')
    setSuccess('')

    try {
      await recibirOrdenCompra(selectedOrden.idOrdenCompra)
      setSuccess('Orden recepcionada correctamente. El inventario del almacén central fue actualizado.')
      setSelectedOrden(null)
      await loadOrdenes()
    } catch (err) {
      setError(getApiErrorMessage(err, 'No se pudo recepcionar la orden de compra'))
    } finally {
      setActionLoading(false)
    }
  }

  const columns = [
    {
      key: 'idOrdenCompra',
      header: 'Orden',
      render: (orden) => <span className="font-semibold text-slate-950">#{orden.idOrdenCompra}</span>
    },
    {
      key: 'proveedor',
      header: 'Proveedor',
      render: (orden) => (
        <div>
          <p className="font-semibold text-slate-900">{orden.proveedor}</p>
          <p className="text-xs text-slate-500">Destino: {orden.ubicacionDestino}</p>
        </div>
      )
    },
    {
      key: 'fechaPedido',
      header: 'Fecha de orden',
      render: (orden) => formatDateTime(orden.fechaPedido)
    },
    {
      key: 'estado',
      header: 'Estado',
      render: (orden) => <Badge tone={getEstadoCompraTone(orden.estado)}>{formatEstadoCompra(orden.estado)}</Badge>
    },
    {
      key: 'totalCompra',
      header: 'Total',
      render: (orden) => <span className="font-bold text-slate-950">{formatMoney(orden.totalCompra)}</span>
    },
    {
      key: 'acciones',
      header: 'Acciones',
      className: 'text-right',
      render: (orden) => (
        <div className="flex justify-end gap-2">
          <Button type="button" variant="secondary" className="px-3 py-2" onClick={() => openDetalle(orden)}>
            Verificar
          </Button>
        </div>
      )
    }
  ]

  if (loading) return <Loader message="Cargando recepciones de compras..." />

  return (
    <div className="space-y-6">
      <PageHeader
        title="Recepciones"
        description="Verifica las órdenes de compra creadas por el Administrador General y confirma la llegada de productos al almacén central."
      />

      {error && <Alert tone="error">{error}</Alert>}
      {success && <Alert tone="success">{success}</Alert>}

      <div className="grid gap-4 md:grid-cols-4">
        <Card title="Órdenes listadas" value={resumen.total} description="Según filtro aplicado" />
        <Card title="Pendientes" value={resumen.pendientes} description="Por verificar" />
        <Card title="Recibidas" value={resumen.recibidas} description="Ya actualizaron inventario" />
        <Card title="Monto pendiente" value={formatMoney(resumen.montoPendiente)} description="Órdenes sin recepción" />
      </div>

      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="grid gap-4 md:grid-cols-2">
          <Input
            label="Buscar"
            placeholder="Orden, proveedor, destino o comprador"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
          <Select label="Estado" value={estado} onChange={(event) => setEstado(event.target.value)}>
            {estadoOptions.map((option) => (
              <option key={option.value || 'todas'} value={option.value}>{option.label}</option>
            ))}
          </Select>
        </div>
      </section>

      <Table
        columns={columns}
        data={filteredOrdenes}
        keyField="idOrdenCompra"
        emptyMessage="No hay órdenes de compra para recepcionar."
      />

      <Modal
        isOpen={Boolean(selectedOrden)}
        onClose={() => setSelectedOrden(null)}
        title={selectedOrden ? `Recepción de orden #${selectedOrden.idOrdenCompra}` : 'Recepción de orden'}
        description={selectedOrden ? `${selectedOrden.proveedor} · ${selectedOrden.ubicacionDestino}` : ''}
        footer={(
          <>
            <Button type="button" variant="secondary" onClick={() => setSelectedOrden(null)}>Cerrar</Button>
            {[ESTADOS_COMPRA.SOLICITADO, ESTADOS_COMPRA.EN_TRANSITO].includes(selectedOrden?.estado) && (
              <Button type="button" disabled={actionLoading} onClick={handleRecibir}>
                {actionLoading ? 'Recepcionando...' : 'Confirmar recepción'}
              </Button>
            )}
          </>
        )}
      >
        {selectedOrden && (
          <div className="space-y-5">
            <div className="grid gap-3 text-sm md:grid-cols-3">
              <div className="rounded-2xl bg-slate-50 p-4">
                <p className="text-slate-500">Estado</p>
                <div className="mt-2"><Badge tone={getEstadoCompraTone(selectedOrden.estado)}>{formatEstadoCompra(selectedOrden.estado)}</Badge></div>
              </div>
              <div className="rounded-2xl bg-slate-50 p-4">
                <p className="text-slate-500">Comprador</p>
                <p className="mt-2 font-semibold text-slate-950">{selectedOrden.usuarioComprador}</p>
              </div>
              <div className="rounded-2xl bg-slate-50 p-4">
                <p className="text-slate-500">Fecha de orden</p>
                <p className="mt-2 font-semibold text-slate-950">{formatDateTime(selectedOrden.fechaPedido)}</p>
              </div>
            </div>

            <Alert tone="warning">
              Antes de confirmar, verifica físicamente que los productos y cantidades hayan llegado al almacén central.
            </Alert>

            <Table
              columns={[
                { key: 'producto', header: 'Producto', render: (detalle) => <div><p className="font-semibold text-slate-900">{detalle.nombreProducto}</p><p className="text-xs text-slate-500">{detalle.codigoBarras}</p></div> },
                { key: 'cantidadPedida', header: 'Cantidad pedida' },
                { key: 'cantidadRecibida', header: 'Cantidad recibida' },
                { key: 'precioCompraUnitario', header: 'Precio', render: (detalle) => formatMoney(detalle.precioCompraUnitario) },
                { key: 'totalLinea', header: 'Total', render: (detalle) => <span className="font-bold text-slate-950">{formatMoney(detalle.totalLinea)}</span> }
              ]}
              data={selectedOrden.detalles || []}
              keyField="idDetalleOrden"
              emptyMessage="Esta orden no tiene detalle."
            />

            <div className="grid gap-3 rounded-2xl border border-slate-200 bg-white p-4 text-sm md:grid-cols-3">
              <div>
                <p className="text-slate-500">Subtotal</p>
                <p className="text-lg font-black text-slate-950">{formatMoney(selectedOrden.totalNeto)}</p>
              </div>
              <div>
                <p className="text-slate-500">IGV</p>
                <p className="text-lg font-black text-slate-950">{formatMoney(selectedOrden.totalIgv)}</p>
              </div>
              <div>
                <p className="text-slate-500">Total</p>
                <p className="text-lg font-black text-slate-950">{formatMoney(selectedOrden.totalCompra)}</p>
              </div>
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}
