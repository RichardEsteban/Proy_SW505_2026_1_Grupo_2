import { useEffect, useMemo, useState } from 'react'
import { listarAlertas, marcarAlertaComoLeida } from '@/shared/api/alertaApi'
import {
  actualizarStockMinimo,
  crearStockInicial,
  listarInventario,
  listarMovimientos,
  registrarMovimiento
} from '@/shared/api/inventarioApi'
import { listarProductos } from '@/shared/api/productoApi'
import { listarUbicaciones } from '@/shared/api/ubicacionApi'
import { useAuth } from '@/shared/auth/AuthContext'
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
import { canSeeAllLocations } from '@/shared/utils/roles'
import {
  canCreateStock,
  canRegisterMovement,
  canUpdateStockMinimo,
  formatDateTime,
  getAlertBadgeTone,
  getApiErrorMessage,
  getStockBadgeTone
} from '@/shared/utils/inventario'

const emptyStockForm = {
  idUbicacion: '',
  idProducto: '',
  stockDisponible: 0,
  stockMinimo: 0
}

const emptyMovimientoForm = {
  idUbicacion: '',
  idProducto: '',
  cantidad: 1,
  tipoMovimiento: 'INGRESO',
  motivoMovimiento: 'AJUSTE'
}

const emptyStockMinimoForm = {
  stockMinimo: 0
}

function normalizeNonNegativeInteger(value) {
  const number = Number(value)
  if (!Number.isFinite(number) || number < 0) return 0
  return Math.floor(number)
}

function normalizePositiveInteger(value) {
  const number = Number(value)
  if (!Number.isFinite(number) || number < 1) return 1
  return Math.floor(number)
}

function sanitizeNonNegativeIntegerInput(value) {
  if (value === '') return ''
  const number = Number(value)
  if (!Number.isFinite(number)) return ''
  if (number < 0) return '0'
  return String(Math.floor(number))
}

function sanitizePositiveIntegerInput(value) {
  if (value === '') return ''
  const number = Number(value)
  if (!Number.isFinite(number)) return ''
  if (number < 1) return '1'
  return String(Math.floor(number))
}

function uniqueLocationsFromInventory(inventario, usuario) {
  const map = new Map()

  if (usuario?.idUbicacion) {
    map.set(usuario.idUbicacion, {
      idUbicacion: usuario.idUbicacion,
      nombreUbicacion: usuario.ubicacion,
      tipoUbicacion: usuario.tipoUbicacion,
      isActivo: true
    })
  }

  inventario.forEach((item) => {
    if (!map.has(item.idUbicacion)) {
      map.set(item.idUbicacion, {
        idUbicacion: item.idUbicacion,
        nombreUbicacion: item.ubicacion,
        tipoUbicacion: item.tipoUbicacion,
        isActivo: true
      })
    }
  })

  return Array.from(map.values())
}

export default function InventarioPage() {
  const { usuario } = useAuth()
  const role = usuario?.rol
  const hasGlobalView = canSeeAllLocations(role)
  const canCreateInitialStock = canCreateStock(role)
  const canCreateMovement = canRegisterMovement(role)
  const canEditStockMinimo = canUpdateStockMinimo(role)

  const [activeTab, setActiveTab] = useState('stock')
  const [inventario, setInventario] = useState([])
  const [movimientos, setMovimientos] = useState([])
  const [alertas, setAlertas] = useState([])
  const [productos, setProductos] = useState([])
  const [ubicaciones, setUbicaciones] = useState([])
  const [selectedUbicacion, setSelectedUbicacion] = useState('')
  const [selectedProducto, setSelectedProducto] = useState('')
  const [soloBajoMinimo, setSoloBajoMinimo] = useState(false)
  const [estadoAlerta, setEstadoAlerta] = useState('PENDIENTE')
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [stockModalOpen, setStockModalOpen] = useState(false)
  const [movimientoModalOpen, setMovimientoModalOpen] = useState(false)
  const [stockMinimoModalOpen, setStockMinimoModalOpen] = useState(false)
  const [selectedInventario, setSelectedInventario] = useState(null)
  const [stockForm, setStockForm] = useState(emptyStockForm)
  const [movimientoForm, setMovimientoForm] = useState(emptyMovimientoForm)
  const [stockMinimoForm, setStockMinimoForm] = useState(emptyStockMinimoForm)

  const ubicacionOptions = useMemo(() => {
    if (ubicaciones.length > 0) return ubicaciones
    return uniqueLocationsFromInventory(inventario, usuario)
  }, [inventario, ubicaciones, usuario])

  const filteredInventario = useMemo(() => {
    const term = search.trim().toLowerCase()

    if (!term) return inventario

    return inventario.filter((item) => (
      item.producto.toLowerCase().includes(term) ||
      item.codigoBarras.toLowerCase().includes(term) ||
      item.ubicacion.toLowerCase().includes(term) ||
      String(item.idProducto).includes(term) ||
      String(item.idInventario).includes(term)
    ))
  }, [inventario, search])

  const resumen = useMemo(() => {
    const stockTotal = inventario.reduce((total, item) => total + Number(item.stockDisponible || 0), 0)
    const bajoMinimo = inventario.filter((item) => item.estadoStock === 'STOCK_MINIMO').length
    const agotados = inventario.filter((item) => item.estadoStock === 'STOCK_AGOTADO').length

    return {
      registros: inventario.length,
      stockTotal,
      bajoMinimo,
      agotados,
      alertasPendientes: alertas.filter((item) => item.estado === 'PENDIENTE').length
    }
  }, [inventario, alertas])

  async function loadCatalogos() {
    try {
      const productosData = await listarProductos({ incluirInactivos: false })
      setProductos(productosData)
    } catch (err) {
      setError(getApiErrorMessage(err, 'No se pudieron cargar los productos'))
    }

    if (hasGlobalView) {
      try {
        const ubicacionesData = await listarUbicaciones({ incluirInactivas: false })
        setUbicaciones(ubicacionesData)
      } catch {
        setUbicaciones([])
      }
    } else if (usuario?.idUbicacion) {
      setUbicaciones([
        {
          idUbicacion: usuario.idUbicacion,
          nombreUbicacion: usuario.ubicacion,
          tipoUbicacion: usuario.tipoUbicacion,
          isActivo: true
        }
      ])
    }
  }

  async function loadInventarioData() {
    setError('')

    const commonFilters = {
      idUbicacion: selectedUbicacion || undefined,
      idProducto: selectedProducto || undefined
    }

    try {
      const [inventarioData, movimientosData, alertasData] = await Promise.all([
        listarInventario({ ...commonFilters, soloBajoMinimo }),
        listarMovimientos({ ...commonFilters, limite: 100 }),
        listarAlertas({ idUbicacion: selectedUbicacion || undefined, estado: estadoAlerta })
      ])

      setInventario(inventarioData)
      setMovimientos(movimientosData)
      setAlertas(alertasData)
    } catch (err) {
      setError(getApiErrorMessage(err, 'No se pudo cargar el inventario'))
    }
  }

  useEffect(() => {
    let isMounted = true

    async function initialLoad() {
      setLoading(true)
      await loadCatalogos()
      if (isMounted) {
        await loadInventarioData()
        setLoading(false)
      }
    }

    initialLoad()

    return () => {
      isMounted = false
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    if (!loading) loadInventarioData()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedUbicacion, selectedProducto, soloBajoMinimo, estadoAlerta])

  function resetMessages() {
    setError('')
    setSuccess('')
  }

  function defaultUbicacionId() {
    return hasGlobalView ? (selectedUbicacion || ubicacionOptions[0]?.idUbicacion || '') : usuario?.idUbicacion || ''
  }

  function defaultProductoId() {
    return selectedProducto || productos[0]?.idProducto || ''
  }

  function openStockModal() {
    resetMessages()
    setStockForm({
      ...emptyStockForm,
      idUbicacion: defaultUbicacionId(),
      idProducto: defaultProductoId()
    })
    setStockModalOpen(true)
  }

  function openMovimientoModal() {
    resetMessages()
    setMovimientoForm({
      ...emptyMovimientoForm,
      idUbicacion: defaultUbicacionId(),
      idProducto: defaultProductoId()
    })
    setMovimientoModalOpen(true)
  }

  function openStockMinimoModal(item) {
    resetMessages()
    setSelectedInventario(item)
    setStockMinimoForm({ stockMinimo: item.stockMinimo })
    setStockMinimoModalOpen(true)
  }

  async function handleCreateStock(event) {
    event.preventDefault()
    setActionLoading(true)
    resetMessages()

    try {
      await crearStockInicial({
        idUbicacion: Number(stockForm.idUbicacion),
        idProducto: Number(stockForm.idProducto),
        stockDisponible: normalizeNonNegativeInteger(stockForm.stockDisponible),
        stockMinimo: normalizeNonNegativeInteger(stockForm.stockMinimo)
      })
      setSuccess('Stock inicial creado correctamente')
      setStockModalOpen(false)
      await loadInventarioData()
    } catch (err) {
      setError(getApiErrorMessage(err, 'No se pudo crear el stock inicial'))
    } finally {
      setActionLoading(false)
    }
  }

  async function handleCreateMovimiento(event) {
    event.preventDefault()
    setActionLoading(true)
    resetMessages()

    try {
      await registrarMovimiento({
        idUbicacion: Number(movimientoForm.idUbicacion),
        idProducto: Number(movimientoForm.idProducto),
        cantidad: normalizePositiveInteger(movimientoForm.cantidad),
        tipoMovimiento: movimientoForm.tipoMovimiento,
        motivoMovimiento: movimientoForm.motivoMovimiento
      })
      setSuccess('Movimiento registrado correctamente')
      setMovimientoModalOpen(false)
      await loadInventarioData()
    } catch (err) {
      setError(getApiErrorMessage(err, 'No se pudo registrar el movimiento'))
    } finally {
      setActionLoading(false)
    }
  }

  async function handleUpdateStockMinimo(event) {
    event.preventDefault()
    if (!selectedInventario) return

    setActionLoading(true)
    resetMessages()

    try {
      await actualizarStockMinimo(selectedInventario.idInventario, {
        stockMinimo: normalizeNonNegativeInteger(stockMinimoForm.stockMinimo)
      })
      setSuccess('Stock mínimo actualizado correctamente')
      setStockMinimoModalOpen(false)
      setSelectedInventario(null)
      await loadInventarioData()
    } catch (err) {
      setError(getApiErrorMessage(err, 'No se pudo actualizar el stock mínimo'))
    } finally {
      setActionLoading(false)
    }
  }

  async function handleMarkAlertRead(alerta) {
    setActionLoading(true)
    resetMessages()

    try {
      await marcarAlertaComoLeida(alerta.idAlerta)
      setSuccess('Alerta marcada como leída')
      await loadInventarioData()
    } catch (err) {
      setError(getApiErrorMessage(err, 'No se pudo marcar la alerta como leída'))
    } finally {
      setActionLoading(false)
    }
  }

  const stockColumns = [
    { key: 'idInventario', header: 'ID', render: (row) => <span className="font-semibold text-slate-900">#{row.idInventario}</span> },
    { key: 'ubicacion', header: 'Ubicación', render: (row) => <div><p className="font-semibold text-slate-900">{row.ubicacion}</p><p className="text-xs text-slate-500">{row.tipoUbicacion}</p></div> },
    { key: 'producto', header: 'Producto', render: (row) => <div><p className="font-semibold text-slate-900">{row.producto}</p><p className="text-xs text-slate-500">{row.codigoBarras}</p></div> },
    { key: 'stockDisponible', header: 'Stock', render: (row) => <span className="text-lg font-black text-slate-900">{row.stockDisponible}</span> },
    { key: 'stockMinimo', header: 'Mínimo' },
    { key: 'estadoStock', header: 'Estado', render: (row) => <Badge tone={getStockBadgeTone(row.estadoStock)}>{row.estadoStock}</Badge> },
    {
      key: 'acciones',
      header: 'Acciones',
      render: (row) => canEditStockMinimo ? (
        <Button type="button" variant="secondary" className="px-3 py-2" onClick={() => openStockMinimoModal(row)}>
          Stock mínimo
        </Button>
      ) : <span className="text-slate-400">Solo lectura</span>
    }
  ]

  const movimientoColumns = [
    { key: 'idMovimiento', header: 'ID', render: (row) => <span className="font-semibold text-slate-900">#{row.idMovimiento}</span> },
    { key: 'fechaHora', header: 'Fecha', render: (row) => formatDateTime(row.fechaHora) },
    { key: 'ubicacion', header: 'Ubicación' },
    { key: 'producto', header: 'Producto', render: (row) => <span className="font-semibold text-slate-900">{row.producto}</span> },
    { key: 'tipoMovimiento', header: 'Tipo', render: (row) => <Badge tone={row.tipoMovimiento === 'INGRESO' ? 'green' : 'red'}>{row.tipoMovimiento}</Badge> },
    { key: 'motivoMovimiento', header: 'Motivo' },
    { key: 'cantidad', header: 'Cantidad', render: (row) => <span className="font-bold text-slate-900">{row.cantidad}</span> },
    { key: 'usuario', header: 'Usuario' }
  ]

  const alertaColumns = [
    { key: 'idAlerta', header: 'ID', render: (row) => <span className="font-semibold text-slate-900">#{row.idAlerta}</span> },
    { key: 'fechaCreacion', header: 'Fecha', render: (row) => formatDateTime(row.fechaCreacion) },
    { key: 'ubicacion', header: 'Ubicación' },
    { key: 'producto', header: 'Producto', render: (row) => <span className="font-semibold text-slate-900">{row.producto}</span> },
    { key: 'tipoAlerta', header: 'Tipo', render: (row) => <Badge tone={getAlertBadgeTone(row.tipoAlerta)}>{row.tipoAlerta}</Badge> },
    { key: 'cantidadActual', header: 'Actual' },
    { key: 'stockReferencia', header: 'Referencia' },
    { key: 'estado', header: 'Estado', render: (row) => <Badge tone={row.estado === 'PENDIENTE' ? 'amber' : 'green'}>{row.estado}</Badge> },
    {
      key: 'acciones',
      header: 'Acciones',
      render: (row) => row.estado === 'PENDIENTE' ? (
        <Button type="button" variant="secondary" className="px-3 py-2" disabled={actionLoading} onClick={() => handleMarkAlertRead(row)}>
          Marcar leída
        </Button>
      ) : <span className="text-slate-400">Sin acciones</span>
    }
  ]

  if (loading) return <Loader message="Cargando inventario..." />

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Inventario"
        title="Stock, kardex y alertas"
        description="Consulta stock por ubicación, crea stock inicial, ajusta stock mínimo, registra movimientos manuales y revisa alertas por stock bajo o agotado."
        actions={(
          <>
            {canCreateInitialStock && <Button onClick={openStockModal}>Stock inicial</Button>}
            {canCreateMovement && <Button variant="secondary" onClick={openMovimientoModal}>Nuevo movimiento</Button>}
          </>
        )}
      />

      {error && <Alert tone="error">{error}</Alert>}
      {success && <Alert tone="success">{success}</Alert>}

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        <Card title="Registros" value={resumen.registros} description="Producto por ubicación" />
        <Card title="Stock total" value={resumen.stockTotal} description="Unidades visibles" />
        <Card title="Stock mínimo" value={resumen.bajoMinimo} description="Registros en mínimo" />
        <Card title="Agotados" value={resumen.agotados} description="Registros sin stock" />
        <Card title="Alertas pendientes" value={resumen.alertasPendientes} description="Por revisar" />
      </section>

      <Card>
        <div className="grid gap-3 lg:grid-cols-5">
          <Input
            label="Buscar"
            placeholder="Producto, código, ubicación o ID"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
          <Select label="Ubicación" value={selectedUbicacion} onChange={(event) => setSelectedUbicacion(event.target.value)} disabled={!hasGlobalView}>
            <option value="">{hasGlobalView ? 'Todas las ubicaciones' : usuario?.ubicacion}</option>
            {ubicacionOptions.map((ubicacion) => (
              <option key={ubicacion.idUbicacion} value={ubicacion.idUbicacion}>{ubicacion.nombreUbicacion}</option>
            ))}
          </Select>
          <Select label="Producto" value={selectedProducto} onChange={(event) => setSelectedProducto(event.target.value)}>
            <option value="">Todos los productos</option>
            {productos.map((producto) => (
              <option key={producto.idProducto} value={producto.idProducto}>{producto.nombreProducto}</option>
            ))}
          </Select>
          <Select label="Alertas" value={estadoAlerta} onChange={(event) => setEstadoAlerta(event.target.value)}>
            <option value="PENDIENTE">Pendientes</option>
            <option value="LEIDA">Leídas</option>
          </Select>
          <label className="flex items-end gap-2 pb-2 text-sm font-medium text-slate-700">
            <input
              type="checkbox"
              checked={soloBajoMinimo}
              onChange={(event) => setSoloBajoMinimo(event.target.checked)}
              className="mb-1 h-4 w-4 rounded border-slate-300"
            />
            Solo bajo mínimo / agotado
          </label>
        </div>
      </Card>

      <div className="flex flex-wrap gap-2">
        {[
          ['stock', 'Stock por ubicación'],
          ['movimientos', 'Movimientos / Kardex'],
          ['alertas', 'Alertas']
        ].map(([key, label]) => (
          <Button
            key={key}
            type="button"
            variant={activeTab === key ? 'primary' : 'secondary'}
            onClick={() => setActiveTab(key)}
          >
            {label}
          </Button>
        ))}
      </div>

      {activeTab === 'stock' && (
        <Table columns={stockColumns} data={filteredInventario} keyField="idInventario" emptyMessage="No hay stock registrado con los filtros actuales." />
      )}

      {activeTab === 'movimientos' && (
        <Table columns={movimientoColumns} data={movimientos} keyField="idMovimiento" emptyMessage="No hay movimientos registrados con los filtros actuales." />
      )}

      {activeTab === 'alertas' && (
        <Table columns={alertaColumns} data={alertas} keyField="idAlerta" emptyMessage="No hay alertas con los filtros actuales." />
      )}

      <Modal
        isOpen={stockModalOpen}
        onClose={() => setStockModalOpen(false)}
        title="Crear stock inicial"
        description="Registra el stock inicial de un producto en una ubicación. Solo se puede crear una vez por producto y ubicación."
        footer={(
          <>
            <Button type="button" variant="secondary" onClick={() => setStockModalOpen(false)}>Cancelar</Button>
            <Button type="submit" form="stock-form" disabled={actionLoading}>{actionLoading ? 'Guardando...' : 'Guardar'}</Button>
          </>
        )}
      >
        <form id="stock-form" className="grid gap-4 md:grid-cols-2" onSubmit={handleCreateStock}>
          <Select label="Ubicación" value={stockForm.idUbicacion} onChange={(event) => setStockForm((prev) => ({ ...prev, idUbicacion: event.target.value }))} required>
            <option value="">Selecciona ubicación</option>
            {ubicacionOptions.map((ubicacion) => (
              <option key={ubicacion.idUbicacion} value={ubicacion.idUbicacion}>{ubicacion.nombreUbicacion}</option>
            ))}
          </Select>
          <Select label="Producto" value={stockForm.idProducto} onChange={(event) => setStockForm((prev) => ({ ...prev, idProducto: event.target.value }))} required>
            <option value="">Selecciona producto</option>
            {productos.map((producto) => (
              <option key={producto.idProducto} value={producto.idProducto}>{producto.nombreProducto}</option>
            ))}
          </Select>
          <Input label="Stock disponible" type="number" min="0" step="1" value={stockForm.stockDisponible} onChange={(event) => setStockForm((prev) => ({ ...prev, stockDisponible: sanitizeNonNegativeIntegerInput(event.target.value) }))} required />
          <Input label="Stock mínimo" type="number" min="0" step="1" value={stockForm.stockMinimo} onChange={(event) => setStockForm((prev) => ({ ...prev, stockMinimo: sanitizeNonNegativeIntegerInput(event.target.value) }))} required />
        </form>
      </Modal>

      <Modal
        isOpen={movimientoModalOpen}
        onClose={() => setMovimientoModalOpen(false)}
        title="Registrar movimiento manual"
        description="Usa esta opción para ajustes o mermas. Las ventas, compras y reposiciones generan movimientos automáticos."
        footer={(
          <>
            <Button type="button" variant="secondary" onClick={() => setMovimientoModalOpen(false)}>Cancelar</Button>
            <Button type="submit" form="movimiento-form" disabled={actionLoading}>{actionLoading ? 'Registrando...' : 'Registrar'}</Button>
          </>
        )}
      >
        <form id="movimiento-form" className="grid gap-4 md:grid-cols-2" onSubmit={handleCreateMovimiento}>
          <Select label="Ubicación" value={movimientoForm.idUbicacion} onChange={(event) => setMovimientoForm((prev) => ({ ...prev, idUbicacion: event.target.value }))} required>
            <option value="">Selecciona ubicación</option>
            {ubicacionOptions.map((ubicacion) => (
              <option key={ubicacion.idUbicacion} value={ubicacion.idUbicacion}>{ubicacion.nombreUbicacion}</option>
            ))}
          </Select>
          <Select label="Producto" value={movimientoForm.idProducto} onChange={(event) => setMovimientoForm((prev) => ({ ...prev, idProducto: event.target.value }))} required>
            <option value="">Selecciona producto</option>
            {productos.map((producto) => (
              <option key={producto.idProducto} value={producto.idProducto}>{producto.nombreProducto}</option>
            ))}
          </Select>
          <Input label="Cantidad" type="number" min="1" step="1" value={movimientoForm.cantidad} onChange={(event) => setMovimientoForm((prev) => ({ ...prev, cantidad: sanitizePositiveIntegerInput(event.target.value) }))} required />
          <Select label="Tipo de movimiento" value={movimientoForm.tipoMovimiento} onChange={(event) => setMovimientoForm((prev) => ({ ...prev, tipoMovimiento: event.target.value }))}>
            <option value="INGRESO">INGRESO</option>
            <option value="SALIDA">SALIDA</option>
          </Select>
          <Select label="Motivo" value={movimientoForm.motivoMovimiento} onChange={(event) => setMovimientoForm((prev) => ({ ...prev, motivoMovimiento: event.target.value }))}>
            <option value="AJUSTE">AJUSTE</option>
            <option value="MERMA">MERMA</option>
          </Select>
        </form>
      </Modal>

      <Modal
        isOpen={stockMinimoModalOpen}
        onClose={() => setStockMinimoModalOpen(false)}
        title="Actualizar stock mínimo"
        description={selectedInventario ? `${selectedInventario.producto} en ${selectedInventario.ubicacion}` : ''}
        footer={(
          <>
            <Button type="button" variant="secondary" onClick={() => setStockMinimoModalOpen(false)}>Cancelar</Button>
            <Button type="submit" form="stock-minimo-form" disabled={actionLoading}>{actionLoading ? 'Guardando...' : 'Guardar'}</Button>
          </>
        )}
      >
        <form id="stock-minimo-form" onSubmit={handleUpdateStockMinimo}>
          <Input
            label="Nuevo stock mínimo"
            type="number"
            min="0"
            step="1"
            value={stockMinimoForm.stockMinimo}
            onChange={(event) => setStockMinimoForm({ stockMinimo: sanitizeNonNegativeIntegerInput(event.target.value) })}
            required
          />
        </form>
      </Modal>
    </div>
  )
}
