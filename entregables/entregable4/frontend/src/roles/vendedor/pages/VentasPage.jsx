import { useEffect, useMemo, useState } from 'react'
import { crearCliente, listarClientes } from '@/shared/api/clienteApi'
import { listarInventario } from '@/shared/api/inventarioApi'
import { listarMetodosPago } from '@/shared/api/metodoPagoApi'
import { listarProductos } from '@/shared/api/productoApi'
import { listarUbicaciones } from '@/shared/api/ubicacionApi'
import { crearVenta, listarVentas } from '@/shared/api/ventaApi'
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
import { formatMoney } from '@/shared/utils/formatMoney'
import { canSeeAllLocations } from '@/shared/utils/roles'
import {
  buildStockMap,
  calculateLine,
  canCreateSale,
  formatDateTime,
  getApiErrorMessage,
  getClienteLabel,
  localDateTimeToIso,
  moneyNumber,
  roundMoney
} from '@/shared/utils/ventas'

const emptyVentaForm = {
  idUbicacion: '',
  idMetodoPago: '',
  idCliente: '',
  detalles: []
}

const emptyClienteForm = {
  tipoCliente: 'PERSONA',
  telefono: '',
  correoElectronico: '',
  documentoIdentidad: '',
  nombres: '',
  apellidos: '',
  identificacionFiscal: '',
  razonSocial: '',
  direccionFiscal: ''
}

function cleanNullable(value) {
  const trimmed = String(value ?? '').trim()
  return trimmed === '' ? null : trimmed
}

function normalizeDateRangeFilter({ desde, hasta }) {
  return {
    desde: localDateTimeToIso(desde),
    hasta: localDateTimeToIso(hasta)
  }
}

export default function VentasPage() {
  const { usuario } = useAuth()
  const role = usuario?.rol
  const hasGlobalView = canSeeAllLocations(role)
  const canRegisterSale = canCreateSale(role)

  const [ventas, setVentas] = useState([])
  const [productos, setProductos] = useState([])
  const [clientes, setClientes] = useState([])
  const [metodosPago, setMetodosPago] = useState([])
  const [ubicaciones, setUbicaciones] = useState([])
  const [inventarioVenta, setInventarioVenta] = useState([])
  const [selectedUbicacion, setSelectedUbicacion] = useState('')
  const [desde, setDesde] = useState('')
  const [hasta, setHasta] = useState('')
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(false)
  const [inventoryLoading, setInventoryLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [ventaModalOpen, setVentaModalOpen] = useState(false)
  const [clienteModalOpen, setClienteModalOpen] = useState(false)
  const [detalleModalOpen, setDetalleModalOpen] = useState(false)
  const [selectedVenta, setSelectedVenta] = useState(null)
  const [ventaForm, setVentaForm] = useState(emptyVentaForm)
  const [clienteForm, setClienteForm] = useState(emptyClienteForm)

  const stockMap = useMemo(() => buildStockMap(inventarioVenta), [inventarioVenta])

  const productosActivos = useMemo(() => productos.filter((producto) => producto.isActivo !== false), [productos])

  const productosParaVenta = useMemo(() => productosActivos.map((producto) => ({
    ...producto,
    stockDisponible: stockMap.get(Number(producto.idProducto)) ?? 0
  })), [productosActivos, stockMap])

  const ubicacionOptions = useMemo(() => {
    if (hasGlobalView) return ubicaciones

    if (!usuario?.idUbicacion) return []

    return [
      {
        idUbicacion: usuario.idUbicacion,
        nombreUbicacion: usuario.ubicacion,
        tipoUbicacion: usuario.tipoUbicacion,
        isActivo: true
      }
    ]
  }, [hasGlobalView, ubicaciones, usuario])

  const filteredVentas = useMemo(() => {
    const term = search.trim().toLowerCase()

    if (!term) return ventas

    return ventas.filter((venta) => (
      String(venta.idVenta).includes(term) ||
      venta.ubicacion?.toLowerCase().includes(term) ||
      venta.usuario?.toLowerCase().includes(term) ||
      venta.cliente?.toLowerCase().includes(term) ||
      venta.metodoPago?.toLowerCase().includes(term)
    ))
  }, [ventas, search])

  const resumen = useMemo(() => {
    const total = filteredVentas.reduce((sum, venta) => sum + moneyNumber(venta.totalVenta), 0)
    const cantidad = filteredVentas.length
    const ticket = cantidad > 0 ? total / cantidad : 0
    const unidades = filteredVentas.reduce((sum, venta) => (
      sum + (venta.detalles || []).reduce((detalleSum, detalle) => detalleSum + Number(detalle.cantidad || 0), 0)
    ), 0)

    return {
      total: roundMoney(total),
      cantidad,
      ticket: roundMoney(ticket),
      unidades
    }
  }, [filteredVentas])

  const totalsPreview = useMemo(() => {
    return ventaForm.detalles.reduce((totals, detalle) => {
      const producto = productos.find((item) => Number(item.idProducto) === Number(detalle.idProducto))
      if (!producto) return totals

      const line = calculateLine({
        precioVenta: producto.precioVenta,
        porcentajeIgv: producto.porcentajeIgv,
        cantidad: detalle.cantidad
      })

      return {
        subtotal: roundMoney(totals.subtotal + line.subtotal),
        igv: roundMoney(totals.igv + line.igv),
        total: roundMoney(totals.total + line.total)
      }
    }, { subtotal: 0, igv: 0, total: 0 })
  }, [productos, ventaForm.detalles])

  async function loadCatalogos() {
    const [productosData, clientesData, metodosData] = await Promise.all([
      listarProductos({ incluirInactivos: false }),
      listarClientes({ incluirInactivos: false }),
      listarMetodosPago({ incluirInactivos: false })
    ])

    setProductos(productosData)
    setClientes(clientesData)
    setMetodosPago(metodosData)

    if (hasGlobalView) {
      try {
        const ubicacionesData = await listarUbicaciones({ incluirInactivas: false })
        setUbicaciones(ubicacionesData)
      } catch {
        setUbicaciones([])
      }
    }
  }

  async function loadVentas() {
    setError('')
    const dateFilters = normalizeDateRangeFilter({ desde, hasta })

    try {
      const data = await listarVentas({
        idUbicacion: selectedUbicacion || undefined,
        desde: dateFilters.desde,
        hasta: dateFilters.hasta,
        limite: 200
      })
      setVentas(data)
    } catch (err) {
      setError(getApiErrorMessage(err, 'No se pudieron cargar las ventas'))
    }
  }

  async function loadInventarioVenta(idUbicacion) {
    if (!idUbicacion) {
      setInventarioVenta([])
      return
    }

    setInventoryLoading(true)

    try {
      const data = await listarInventario({ idUbicacion })
      setInventarioVenta(data)
    } catch {
      setInventarioVenta([])
    } finally {
      setInventoryLoading(false)
    }
  }

  useEffect(() => {
    let isMounted = true

    async function initialLoad() {
      setLoading(true)
      setError('')

      try {
        await loadCatalogos()
        if (isMounted) await loadVentas()
      } catch (err) {
        if (isMounted) setError(getApiErrorMessage(err, 'No se pudo cargar el módulo de ventas'))
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
    if (!loading) loadVentas()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedUbicacion, desde, hasta])

  useEffect(() => {
    if (ventaModalOpen) {
      loadInventarioVenta(ventaForm.idUbicacion)
    }
  }, [ventaModalOpen, ventaForm.idUbicacion])

  function resetMessages() {
    setError('')
    setSuccess('')
  }

  function defaultUbicacionId() {
    if (!hasGlobalView) return usuario?.idUbicacion || ''
    return selectedUbicacion || ubicacionOptions[0]?.idUbicacion || ''
  }

  function defaultMetodoPagoId() {
    return metodosPago[0]?.idMetodoPago || ''
  }

  function openVentaModal() {
    resetMessages()
    setVentaForm({
      ...emptyVentaForm,
      idUbicacion: defaultUbicacionId(),
      idMetodoPago: defaultMetodoPagoId(),
      detalles: []
    })
    setVentaModalOpen(true)
  }

  function openClienteModal() {
    resetMessages()
    setClienteForm(emptyClienteForm)
    setClienteModalOpen(true)
  }

  function openDetalleModal(venta) {
    setSelectedVenta(venta)
    setDetalleModalOpen(true)
  }

  function updateVentaForm(name, value) {
    setVentaForm((prev) => ({ ...prev, [name]: value }))
  }
  function validateVenta() {
    if (!ventaForm.idMetodoPago) return 'Selecciona un método de pago'
    if (!ventaForm.idUbicacion) return 'Selecciona una ubicación'

    const detallesValidos = ventaForm.detalles.filter((detalle) => detalle.idProducto && Number(detalle.cantidad) > 0)
    if (detallesValidos.length === 0) return 'Agrega al menos un producto con cantidad válida'

    for (const detalle of detallesValidos) {
      const stockDisponible = stockMap.get(Number(detalle.idProducto))
      if (stockDisponible !== undefined && Number(detalle.cantidad) > stockDisponible) {
        const producto = productos.find((item) => Number(item.idProducto) === Number(detalle.idProducto))
        return `Stock insuficiente para ${producto?.nombreProducto || 'el producto seleccionado'}`
      }
    }

    return ''
  }

  async function handleCreateVenta(event) {
    event.preventDefault()
    setActionLoading(true)
    resetMessages()

    const validationError = validateVenta()
    if (validationError) {
      setError(validationError)
      setActionLoading(false)
      return
    }

    try {
      const payload = {
        idMetodoPago: Number(ventaForm.idMetodoPago),
        idCliente: ventaForm.idCliente ? Number(ventaForm.idCliente) : null,
        idUbicacion: ventaForm.idUbicacion ? Number(ventaForm.idUbicacion) : null,
        detalles: ventaForm.detalles
          .filter((detalle) => detalle.idProducto && Number(detalle.cantidad) > 0)
          .map((detalle) => ({
            idProducto: Number(detalle.idProducto),
            cantidad: Number(detalle.cantidad)
          }))
      }

      const ventaCreada = await crearVenta(payload)
      setSuccess(`Venta #${ventaCreada.idVenta} registrada correctamente`)
      setVentaModalOpen(false)
      await Promise.all([
        loadVentas(),
        loadInventarioVenta(ventaForm.idUbicacion)
      ])
    } catch (err) {
      setError(getApiErrorMessage(err, 'No se pudo registrar la venta'))
    } finally {
      setActionLoading(false)
    }
  }

  async function handleCreateCliente(event) {
    event.preventDefault()
    setActionLoading(true)
    resetMessages()

    try {
      const payload = {
        tipoCliente: clienteForm.tipoCliente,
        telefono: cleanNullable(clienteForm.telefono),
        correoElectronico: cleanNullable(clienteForm.correoElectronico),
        documentoIdentidad: clienteForm.tipoCliente === 'PERSONA' ? cleanNullable(clienteForm.documentoIdentidad) : null,
        nombres: clienteForm.tipoCliente === 'PERSONA' ? cleanNullable(clienteForm.nombres) : null,
        apellidos: clienteForm.tipoCliente === 'PERSONA' ? cleanNullable(clienteForm.apellidos) : null,
        identificacionFiscal: clienteForm.tipoCliente === 'EMPRESA' ? cleanNullable(clienteForm.identificacionFiscal) : null,
        razonSocial: clienteForm.tipoCliente === 'EMPRESA' ? cleanNullable(clienteForm.razonSocial) : null,
        direccionFiscal: clienteForm.tipoCliente === 'EMPRESA' ? cleanNullable(clienteForm.direccionFiscal) : null
      }

      const clienteCreado = await crearCliente(payload)
      setClientes((prev) => [clienteCreado, ...prev])
      setVentaForm((prev) => ({ ...prev, idCliente: clienteCreado.idCliente }))
      setClienteModalOpen(false)
      setSuccess(`Cliente ${getClienteLabel(clienteCreado)} creado correctamente`)
    } catch (err) {
      setError(getApiErrorMessage(err, 'No se pudo crear el cliente'))
    } finally {
      setActionLoading(false)
    }
  }

  function clearFilters() {
    setSelectedUbicacion('')
    setDesde('')
    setHasta('')
    setSearch('')
  }

  const ventasColumns = [
    { key: 'idVenta', header: 'Venta', render: (row) => <span className="font-semibold text-slate-900">#{row.idVenta}</span> },
    { key: 'fechaHora', header: 'Fecha', render: (row) => formatDateTime(row.fechaHora) },
    { key: 'ubicacion', header: 'Ubicación', render: (row) => <div><p className="font-semibold text-slate-900">{row.ubicacion}</p><p className="text-xs text-slate-500">{row.usuario}</p></div> },
    { key: 'cliente', header: 'Cliente', render: (row) => row.cliente || <span className="text-slate-400">Sin cliente</span> },
    { key: 'metodoPago', header: 'Pago', render: (row) => <Badge>{row.metodoPago}</Badge> },
    { key: 'totalVenta', header: 'Total', render: (row) => <span className="text-base font-black text-slate-950">{formatMoney(row.totalVenta)}</span> },
    { key: 'acciones', header: 'Acciones', render: (row) => <Button type="button" variant="secondary" className="px-3 py-2" onClick={() => openDetalleModal(row)}>Ver detalle</Button> }
  ]

  const detalleColumns = [
    { key: 'idDetalleVenta', header: 'ID', render: (row) => <span className="font-semibold text-slate-900">#{row.idDetalleVenta}</span> },
    { key: 'nombreProducto', header: 'Producto', render: (row) => <div><p className="font-semibold text-slate-900">{row.nombreProducto}</p><p className="text-xs text-slate-500">{row.codigoBarras}</p></div> },
    { key: 'cantidad', header: 'Cantidad' },
    { key: 'precioUnitarioFacturado', header: 'Precio', render: (row) => formatMoney(row.precioUnitarioFacturado) },
    { key: 'subtotal', header: 'Subtotal', render: (row) => formatMoney(row.subtotal) },
    { key: 'igvAplicado', header: 'IGV', render: (row) => formatMoney(row.igvAplicado) },
    { key: 'totalLinea', header: 'Total', render: (row) => <span className="font-bold text-slate-900">{formatMoney(row.totalLinea)}</span> }
  ]

  if (loading) return <Loader message="Cargando ventas..." />

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Ventas"
        title="Registro e historial de ventas"
        description="Registra ventas, selecciona productos, calcula subtotales e IGV y deja que el backend descuente el stock automáticamente con movimiento de kardex por venta."
        actions={canRegisterSale && <Button onClick={openVentaModal}>Nueva venta</Button>}
      />

      {error && <Alert tone="error">{error}</Alert>}
      {success && <Alert tone="success">{success}</Alert>}

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Card title="Ventas" value={resumen.cantidad} description="Registros filtrados" />
        <Card title="Total vendido" value={formatMoney(resumen.total)} description="Suma de ventas" />
        <Card title="Ticket promedio" value={formatMoney(resumen.ticket)} description="Promedio por venta" />
        <Card title="Unidades vendidas" value={resumen.unidades} description="Productos facturados" />
      </section>

      <Card>
        <div className="grid gap-3 lg:grid-cols-5">
          <Input
            label="Buscar"
            placeholder="ID, cliente, usuario, método o ubicación"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
          <Select label="Ubicación" value={selectedUbicacion} onChange={(event) => setSelectedUbicacion(event.target.value)} disabled={!hasGlobalView}>
            <option value="">{hasGlobalView ? 'Todas las ubicaciones' : usuario?.ubicacion}</option>
            {ubicacionOptions.map((ubicacion) => (
              <option key={ubicacion.idUbicacion} value={ubicacion.idUbicacion}>{ubicacion.nombreUbicacion}</option>
            ))}
          </Select>
          <Input label="Desde" type="datetime-local" value={desde} onChange={(event) => setDesde(event.target.value)} />
          <Input label="Hasta" type="datetime-local" value={hasta} onChange={(event) => setHasta(event.target.value)} />
          <div className="flex items-end">
            <Button type="button" variant="secondary" className="w-full" onClick={clearFilters}>Limpiar filtros</Button>
          </div>
        </div>
      </Card>

      <Table columns={ventasColumns} data={filteredVentas} keyField="idVenta" emptyMessage="No hay ventas registradas con los filtros actuales." />

      <Modal
        isOpen={ventaModalOpen}
        onClose={() => setVentaModalOpen(false)}
        size="xl"
        title="Registrar nueva venta"
        description="Selecciona ubicación, método de pago, cliente opcional y productos. El stock se validará antes de guardar."
        footer={(
          <>
            <Button type="button" variant="secondary" onClick={() => setVentaModalOpen(false)}>Cancelar</Button>
            <Button type="submit" form="venta-form" disabled={actionLoading || inventoryLoading}>{actionLoading ? 'Registrando...' : 'Registrar venta'}</Button>
          </>
        )}
      >
        <form id="venta-form" className="space-y-5" onSubmit={handleCreateVenta}>
          <div className="grid gap-4 md:grid-cols-2">
            <Select label="Ubicación de venta" value={ventaForm.idUbicacion} onChange={(event) => updateVentaForm('idUbicacion', event.target.value)} disabled={!hasGlobalView} required>
              <option value="">Selecciona ubicación</option>
              {ubicacionOptions.map((ubicacion) => (
                <option key={ubicacion.idUbicacion} value={ubicacion.idUbicacion}>{ubicacion.nombreUbicacion}</option>
              ))}
            </Select>
            <Select label="Método de pago" value={ventaForm.idMetodoPago} onChange={(event) => updateVentaForm('idMetodoPago', event.target.value)} required>
              <option value="">Selecciona método</option>
              {metodosPago.map((metodo) => (
                <option key={metodo.idMetodoPago} value={metodo.idMetodoPago}>{metodo.nombreMetodo}</option>
              ))}
            </Select>
          </div>

          <div className="grid gap-3 md:grid-cols-[1fr_auto] md:items-end">
            <Select label="Cliente opcional" value={ventaForm.idCliente} onChange={(event) => updateVentaForm('idCliente', event.target.value)}>
              <option value="">Venta sin cliente</option>
              {clientes.map((cliente) => (
                <option key={cliente.idCliente} value={cliente.idCliente}>{getClienteLabel(cliente)}</option>
              ))}
            </Select>
            <Button type="button" variant="secondary" onClick={openClienteModal}>Nuevo cliente</Button>
          </div>

          {inventoryLoading && <Alert>Consultando stock disponible...</Alert>}

          <ProductPicker
            title="Buscar productos para la venta"
            description="Busca por nombre o código, filtra por categoría y agrega productos al carrito de venta."
            products={productosParaVenta}
            selectedItems={ventaForm.detalles}
            onChange={(detalles) => setVentaForm((prev) => ({ ...prev, detalles }))}
            quantityField="cantidad"
            quantityLabel="Cantidad"
            selectedTitle="Carrito de venta"
            addButtonLabel="Agregar"
            showStock
            showUnitPrice
            showLineTotal
            requireAvailableStock
            selectedEmptyMessage="Agrega al menos un producto a la venta."
          />

          <section className="grid gap-3 md:grid-cols-3">
            <Card title="Subtotal" value={formatMoney(totalsPreview.subtotal)} description="Base imponible estimada" />
            <Card title="IGV" value={formatMoney(totalsPreview.igv)} description="Incluido en el precio" />
            <Card title="Total" value={formatMoney(totalsPreview.total)} description="Monto a cobrar" />
          </section>
        </form>
      </Modal>

      <Modal
        isOpen={clienteModalOpen}
        onClose={() => setClienteModalOpen(false)}
        title="Nuevo cliente"
        description="Registra un cliente persona o empresa y selecciónalo automáticamente en la venta."
        footer={(
          <>
            <Button type="button" variant="secondary" onClick={() => setClienteModalOpen(false)}>Cancelar</Button>
            <Button type="submit" form="cliente-form" disabled={actionLoading}>{actionLoading ? 'Guardando...' : 'Guardar cliente'}</Button>
          </>
        )}
      >
        <form id="cliente-form" className="space-y-4" onSubmit={handleCreateCliente}>
          <div className="grid gap-4 md:grid-cols-2">
            <Select label="Tipo de cliente" value={clienteForm.tipoCliente} onChange={(event) => setClienteForm((prev) => ({ ...prev, tipoCliente: event.target.value }))}>
              <option value="PERSONA">Persona</option>
              <option value="EMPRESA">Empresa</option>
            </Select>
            <Input label="Correo electrónico" type="email" value={clienteForm.correoElectronico} onChange={(event) => setClienteForm((prev) => ({ ...prev, correoElectronico: event.target.value }))} />
            <Input label="Teléfono" value={clienteForm.telefono} onChange={(event) => setClienteForm((prev) => ({ ...prev, telefono: event.target.value }))} maxLength={20} />
          </div>

          {clienteForm.tipoCliente === 'PERSONA' ? (
            <div className="grid gap-4 md:grid-cols-3">
              <Input label="Documento" value={clienteForm.documentoIdentidad} onChange={(event) => setClienteForm((prev) => ({ ...prev, documentoIdentidad: event.target.value }))} maxLength={12} required />
              <Input label="Nombres" value={clienteForm.nombres} onChange={(event) => setClienteForm((prev) => ({ ...prev, nombres: event.target.value }))} maxLength={100} required />
              <Input label="Apellidos" value={clienteForm.apellidos} onChange={(event) => setClienteForm((prev) => ({ ...prev, apellidos: event.target.value }))} maxLength={100} required />
            </div>
          ) : (
            <div className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <Input label="RUC" value={clienteForm.identificacionFiscal} onChange={(event) => setClienteForm((prev) => ({ ...prev, identificacionFiscal: event.target.value }))} maxLength={11} required />
                <Input label="Razón social" value={clienteForm.razonSocial} onChange={(event) => setClienteForm((prev) => ({ ...prev, razonSocial: event.target.value }))} maxLength={150} required />
              </div>
              <Textarea label="Dirección fiscal" value={clienteForm.direccionFiscal} onChange={(event) => setClienteForm((prev) => ({ ...prev, direccionFiscal: event.target.value }))} maxLength={255} />
            </div>
          )}
        </form>
      </Modal>

      <Modal
        isOpen={detalleModalOpen}
        onClose={() => setDetalleModalOpen(false)}
        title={selectedVenta ? `Detalle de venta #${selectedVenta.idVenta}` : 'Detalle de venta'}
        description={selectedVenta ? `${formatDateTime(selectedVenta.fechaHora)} · ${selectedVenta.ubicacion}` : ''}
        footer={<Button type="button" variant="secondary" onClick={() => setDetalleModalOpen(false)}>Cerrar</Button>}
      >
        {selectedVenta && (
          <div className="space-y-5">
            <section className="grid gap-3 md:grid-cols-4">
              <Card title="Cliente" value={selectedVenta.cliente || 'Sin cliente'} description={selectedVenta.metodoPago} />
              <Card title="Subtotal" value={formatMoney(selectedVenta.subtotalVenta)} description="Base imponible" />
              <Card title="IGV" value={formatMoney(selectedVenta.totalIgv)} description="Impuesto" />
              <Card title="Total" value={formatMoney(selectedVenta.totalVenta)} description="Cobrado" />
            </section>
            <Table columns={detalleColumns} data={selectedVenta.detalles || []} keyField="idDetalleVenta" emptyMessage="Esta venta no tiene detalle registrado." />
          </div>
        )}
      </Modal>
    </div>
  )
}
