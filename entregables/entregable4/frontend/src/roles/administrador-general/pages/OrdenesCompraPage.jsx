import { useEffect, useMemo, useState } from 'react'
import { cancelarOrdenCompra, crearOrdenCompra, listarOrdenesCompra } from '@/shared/api/ordenCompraApi'
import { listarProductos } from '@/shared/api/productoApi'
import { listarProveedores } from '@/shared/api/proveedorApi'
import { listarUbicaciones } from '@/shared/api/ubicacionApi'
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
import { formatMoney } from '@/shared/utils/formatMoney'
import { isCentralWarehouse } from '@/shared/utils/roleViews'
import {
  ESTADOS_COMPRA,
  calculatePurchaseLine,
  formatDateTime,
  formatEstadoCompra,
  getApiErrorMessage,
  getEstadoCompraTone,
  moneyNumber,
  roundMoney,
  toIsoFromLocalDateTime
} from '@/shared/utils/compras'

const emptyForm = {
  idProveedor: '',
  idUbicacionDestino: '',
  detalles: []
}

const estadoOptions = [
  { value: '', label: 'Todos los estados' },
  { value: ESTADOS_COMPRA.SOLICITADO, label: 'Pendiente de recepción' },
  { value: ESTADOS_COMPRA.EN_TRANSITO, label: 'En tránsito' },
  { value: ESTADOS_COMPRA.RECIBIDO, label: 'Recibida' },
  { value: ESTADOS_COMPRA.CANCELADO, label: 'Cancelada' }
]

export default function OrdenesCompraPage() {
  const [ordenes, setOrdenes] = useState([])
  const [proveedores, setProveedores] = useState([])
  const [productos, setProductos] = useState([])
  const [ubicaciones, setUbicaciones] = useState([])
  const [estado, setEstado] = useState('')
  const [idProveedor, setIdProveedor] = useState('')
  const [desde, setDesde] = useState('')
  const [hasta, setHasta] = useState('')
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [modalOpen, setModalOpen] = useState(false)
  const [detalleModalOpen, setDetalleModalOpen] = useState(false)
  const [selectedOrden, setSelectedOrden] = useState(null)
  const [form, setForm] = useState(emptyForm)
  const [cancelModalOpen, setCancelModalOpen] = useState(false)
  const [ordenToCancel, setOrdenToCancel] = useState(null)
  const [motivoCancelacion, setMotivoCancelacion] = useState('')

  const proveedoresActivos = useMemo(() => proveedores.filter((proveedor) => proveedor.isActivo !== false), [proveedores])
  const productosActivos = useMemo(() => productos.filter((producto) => producto.isActivo !== false), [productos])
  const almacenesCentrales = useMemo(() => ubicaciones.filter((ubicacion) => ubicacion.isActivo !== false && isCentralWarehouse(ubicacion)), [ubicaciones])
  const ubicacionDestinoNombre = useMemo(() => {
    const selected = ubicaciones.find((ubicacion) => Number(ubicacion.idUbicacion) === Number(form.idUbicacionDestino))
    return selected?.nombreUbicacion || 'Almacén Central'
  }, [form.idUbicacionDestino, ubicaciones])

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
    cantidad: filteredOrdenes.length,
    total: roundMoney(filteredOrdenes.reduce((sum, orden) => sum + moneyNumber(orden.totalCompra), 0)),
    pendientes: filteredOrdenes.filter((orden) => orden.estado === ESTADOS_COMPRA.SOLICITADO).length,
    recibidas: filteredOrdenes.filter((orden) => orden.estado === ESTADOS_COMPRA.RECIBIDO).length
  }), [filteredOrdenes])

  const formTotals = useMemo(() => {
    return form.detalles.reduce((totals, detalle) => {
      const producto = productos.find((item) => Number(item.idProducto) === Number(detalle.idProducto))
      if (!producto) return totals

      const line = calculatePurchaseLine({
        precioCompraUnitario: detalle.precioCompraUnitario,
        cantidad: detalle.cantidadPedida,
        porcentajeIgv: producto.porcentajeIgv
      })

      return {
        subtotal: roundMoney(totals.subtotal + line.subtotal),
        igv: roundMoney(totals.igv + line.igv),
        total: roundMoney(totals.total + line.total)
      }
    }, { subtotal: 0, igv: 0, total: 0 })
  }, [form.detalles, productos])

  async function loadCatalogos() {
    const [proveedoresData, productosData, ubicacionesData] = await Promise.all([
      listarProveedores({ incluirInactivos: false }),
      listarProductos({ incluirInactivos: false }),
      listarUbicaciones({ incluirInactivas: false })
    ])

    setProveedores(proveedoresData)
    setProductos(productosData)
    setUbicaciones(ubicacionesData)

    const almacenCentral = ubicacionesData.find((ubicacion) => ubicacion.isActivo !== false && isCentralWarehouse(ubicacion))
    if (almacenCentral) {
      setForm((current) => ({ ...current, idUbicacionDestino: String(almacenCentral.idUbicacion) }))
    }
  }

  async function loadOrdenes() {
    setError('')

    try {
      const data = await listarOrdenesCompra({
        estado: estado || undefined,
        idProveedor: idProveedor || undefined,
        desde: toIsoFromLocalDateTime(desde),
        hasta: toIsoFromLocalDateTime(hasta),
        limite: 200
      })
      setOrdenes(data)
    } catch (err) {
      setError(getApiErrorMessage(err, 'No se pudieron cargar las órdenes de compra'))
    }
  }

  useEffect(() => {
    let isMounted = true

    async function initialLoad() {
      setLoading(true)
      setError('')

      try {
        await loadCatalogos()
        if (isMounted) await loadOrdenes()
      } catch (err) {
        if (isMounted) setError(getApiErrorMessage(err, 'No se pudo cargar el módulo de órdenes de compra'))
      } finally {
        if (isMounted) setLoading(false)
      }
    }

    initialLoad()

    return () => {
      isMounted = false
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    if (!loading) loadOrdenes()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [estado, idProveedor, desde, hasta])

  function resetMessages() {
    setError('')
    setSuccess('')
  }

  function getDefaultWarehouseId() {
    return String(almacenesCentrales[0]?.idUbicacion || form.idUbicacionDestino || '')
  }

  function openCreateModal() {
    resetMessages()
    setForm({
      ...emptyForm,
      idUbicacionDestino: getDefaultWarehouseId()
    })
    setModalOpen(true)
  }
  function validateForm() {
    if (!form.idProveedor) return 'Selecciona un proveedor.'
    if (!form.idUbicacionDestino) return 'No se encontró un almacén central activo como destino.'
    if (!form.detalles.length) return 'Agrega al menos un producto a la orden.'

    for (const detalle of form.detalles) {
      if (!detalle.idProducto) return 'Selecciona un producto en cada línea.'
      if (Number(detalle.cantidadPedida) <= 0) return 'La cantidad pedida debe ser mayor que cero.'
      if (Number(detalle.precioCompraUnitario) <= 0 || detalle.precioCompraUnitario === '') {
        return 'El precio de compra debe ser mayor que cero.'
      }
    }

    return ''
  }

  async function handleCreateOrden(event) {
    event.preventDefault()
    resetMessages()

    const validationError = validateForm()
    if (validationError) {
      setError(validationError)
      return
    }

    setActionLoading(true)

    try {
      const payload = {
        idProveedor: Number(form.idProveedor),
        idUbicacionDestino: Number(form.idUbicacionDestino),
        detalles: form.detalles.map((detalle) => ({
          idProducto: Number(detalle.idProducto),
          cantidadPedida: Number(detalle.cantidadPedida),
          precioCompraUnitario: Number(detalle.precioCompraUnitario)
        }))
      }

      await crearOrdenCompra(payload)
      setModalOpen(false)
      setSuccess('Orden de compra creada. Queda pendiente de recepción por el Supervisor de Almacén Central.')
      await loadOrdenes()
    } catch (err) {
      setError(getApiErrorMessage(err, 'No se pudo crear la orden de compra'))
    } finally {
      setActionLoading(false)
    }
  }

  function openDetalle(orden) {
    setSelectedOrden(orden)
    setDetalleModalOpen(true)
  }

  function openCancelModal(orden) {
    resetMessages()
    setOrdenToCancel(orden)
    setMotivoCancelacion('')
    setCancelModalOpen(true)
  }

  async function handleCancelOrden(event) {
    event.preventDefault()
    if (!ordenToCancel) return

    setActionLoading(true)
    resetMessages()

    try {
      await cancelarOrdenCompra(ordenToCancel.idOrdenCompra, motivoCancelacion)
      setSuccess('Orden de compra cancelada correctamente.')
      await loadOrdenes()
      setCancelModalOpen(false)
      setOrdenToCancel(null)
      setMotivoCancelacion('')
    } catch (err) {
      setError(getApiErrorMessage(err, 'No se pudo cancelar la orden de compra'))
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
      header: 'Fecha',
      render: (orden) => (
        <div>
          <p>{formatDateTime(orden.fechaPedido)}</p>
          {orden.fechaRecepcion && <p className="text-xs text-slate-500">Recibida: {formatDateTime(orden.fechaRecepcion)}</p>}
        </div>
      )
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
        <div className="flex flex-wrap justify-end gap-2">
          <Button type="button" variant="secondary" className="px-3 py-2" onClick={() => openDetalle(orden)}>
            Ver
          </Button>
          {orden.estado === ESTADOS_COMPRA.SOLICITADO && (
            <Button type="button" variant="danger" className="px-3 py-2" disabled={actionLoading} onClick={() => openCancelModal(orden)}>
              Cancelar
            </Button>
          )}
        </div>
      )
    }
  ]

  if (loading) return <Loader message="Cargando órdenes de compra..." />

  return (
    <div className="space-y-6">
      <PageHeader
        title="Órdenes de compra"
        description="El Administrador General genera órdenes para proveedores. El stock no cambia hasta que el Supervisor de Almacén Central recepciona la mercadería."
        action={(
          <Button type="button" onClick={openCreateModal}>
            Nueva orden de compra
          </Button>
        )}
      />

      {error && <Alert tone="error">{error}</Alert>}
      {success && <Alert tone="success">{success}</Alert>}

      <div className="grid gap-4 md:grid-cols-4">
        <Card title="Órdenes" value={resumen.cantidad} description="Según filtros aplicados" />
        <Card title="Total ordenado" value={formatMoney(resumen.total)} description="Importe acumulado" />
        <Card title="Pendientes" value={resumen.pendientes} description="Esperando recepción" />
        <Card title="Recibidas" value={resumen.recibidas} description="Ya actualizaron inventario" />
      </div>

      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="grid gap-4 lg:grid-cols-5">
          <Input
            label="Buscar"
            placeholder="Proveedor, destino, estado o ID"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
          <Select label="Estado" value={estado} onChange={(event) => setEstado(event.target.value)}>
            {estadoOptions.map((option) => (
              <option key={option.value || 'todos'} value={option.value}>{option.label}</option>
            ))}
          </Select>
          <Select label="Proveedor" value={idProveedor} onChange={(event) => setIdProveedor(event.target.value)}>
            <option value="">Todos</option>
            {proveedores.map((proveedor) => (
              <option key={proveedor.idProveedor} value={proveedor.idProveedor}>{proveedor.razonSocial}</option>
            ))}
          </Select>
          <Input label="Desde" type="datetime-local" value={desde} onChange={(event) => setDesde(event.target.value)} />
          <Input label="Hasta" type="datetime-local" value={hasta} onChange={(event) => setHasta(event.target.value)} />
        </div>
      </section>

      <Table
        columns={columns}
        data={filteredOrdenes}
        keyField="idOrdenCompra"
        emptyMessage="No hay órdenes de compra para mostrar."
      />

      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        size="xl"
        title="Nueva orden de compra"
        description={`Destino: ${ubicacionDestinoNombre}. Registra proveedor, productos, cantidades y precios con IGV incluido; el sistema separa subtotal e IGV y el stock se actualizará recién al recepcionar.`}
        footer={(
          <>
            <Button type="button" variant="secondary" onClick={() => setModalOpen(false)}>Cancelar</Button>
            <Button type="submit" form="orden-compra-admin-form" disabled={actionLoading}>{actionLoading ? 'Guardando...' : 'Crear orden de compra'}</Button>
          </>
        )}
      >
        <form id="orden-compra-admin-form" className="space-y-5" onSubmit={handleCreateOrden}>
          <div className="grid gap-4 md:grid-cols-2">
            <Select label="Proveedor" value={form.idProveedor} onChange={(event) => setForm((current) => ({ ...current, idProveedor: event.target.value }))} required>
              <option value="">Seleccionar proveedor</option>
              {proveedoresActivos.map((proveedor) => (
                <option key={proveedor.idProveedor} value={proveedor.idProveedor}>{proveedor.razonSocial}</option>
              ))}
            </Select>
            <Select label="Destino" value={form.idUbicacionDestino} onChange={(event) => setForm((current) => ({ ...current, idUbicacionDestino: event.target.value }))} required>
              <option value="">Seleccionar almacén</option>
              {almacenesCentrales.map((ubicacion) => (
                <option key={ubicacion.idUbicacion} value={ubicacion.idUbicacion}>{ubicacion.nombreUbicacion}</option>
              ))}
            </Select>
          </div>

          <ProductPicker
            title="Buscar productos para la orden"
            description="Filtra por categoría, busca por nombre o código y agrega productos al detalle sin crear líneas una por una."
            products={productosActivos}
            selectedItems={form.detalles}
            onChange={(detalles) => setForm((current) => ({ ...current, detalles }))}
            quantityField="cantidadPedida"
            quantityLabel="Cantidad"
            priceField="precioCompraUnitario"
            priceLabel="Precio compra con IGV"
            selectedTitle="Detalle de la orden"
            addButtonLabel="Agregar"
            showUnitPrice
            showLineTotal
            selectedEmptyMessage="Agrega al menos un producto a la orden."
          />

          <div className="grid gap-3 rounded-2xl border border-slate-200 bg-white p-4 text-sm md:grid-cols-3">
            <div>
              <p className="text-slate-500">Subtotal</p>
              <p className="text-lg font-black text-slate-950">{formatMoney(formTotals.subtotal)}</p>
            </div>
            <div>
              <p className="text-slate-500">IGV</p>
              <p className="text-lg font-black text-slate-950">{formatMoney(formTotals.igv)}</p>
            </div>
            <div>
              <p className="text-slate-500">Total</p>
              <p className="text-lg font-black text-slate-950">{formatMoney(formTotals.total)}</p>
            </div>
          </div>
        </form>
      </Modal>

      <Modal
        isOpen={detalleModalOpen}
        onClose={() => setDetalleModalOpen(false)}
        title={selectedOrden ? `Orden #${selectedOrden.idOrdenCompra}` : 'Detalle de orden'}
        description={selectedOrden ? `${selectedOrden.proveedor} · ${selectedOrden.ubicacionDestino}` : ''}
        footer={<Button type="button" variant="secondary" onClick={() => setDetalleModalOpen(false)}>Cerrar</Button>}
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
                <p className="text-slate-500">Receptor</p>
                <p className="mt-2 font-semibold text-slate-950">{selectedOrden.usuarioReceptor || '-'}</p>
              </div>
            </div>

            <Table
              columns={[
                { key: 'producto', header: 'Producto', render: (detalle) => <div><p className="font-semibold text-slate-900">{detalle.nombreProducto}</p><p className="text-xs text-slate-500">{detalle.codigoBarras}</p></div> },
                { key: 'cantidadPedida', header: 'Pedida' },
                { key: 'cantidadRecibida', header: 'Recibida' },
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

      <Modal
        isOpen={cancelModalOpen}
        onClose={() => setCancelModalOpen(false)}
        title="Cancelar orden de compra"
        description={ordenToCancel ? `Orden #${ordenToCancel.idOrdenCompra} · ${ordenToCancel.proveedor}` : ''}
        footer={(
          <>
            <Button type="button" variant="secondary" onClick={() => setCancelModalOpen(false)}>Volver</Button>
            <Button type="submit" form="cancelar-orden-admin-form" variant="danger" disabled={actionLoading}>{actionLoading ? 'Cancelando...' : 'Cancelar orden'}</Button>
          </>
        )}
      >
        <form id="cancelar-orden-admin-form" onSubmit={handleCancelOrden}>
          <Textarea
            label="Motivo opcional"
            placeholder="Ejemplo: proveedor no entregará la mercadería"
            value={motivoCancelacion}
            onChange={(event) => setMotivoCancelacion(event.target.value)}
            rows={4}
          />
        </form>
      </Modal>
    </div>
  )
}
