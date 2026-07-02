import { useEffect, useMemo, useState } from 'react'
import {
  listarComprasReporte,
  listarKardexReporte,
  listarProductosMasVendidos,
  listarReposicionesPorEstado,
  listarStockBajoReporte,
  listarVentasPorFecha,
  obtenerResumenReporte
} from '@/shared/api/reporteApi'
import { listarProductos } from '@/shared/api/productoApi'
import { listarUbicaciones } from '@/shared/api/ubicacionApi'
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
import { formatMoney } from '@/shared/utils/formatMoney'
import { ROLES, canSeeAllLocations } from '@/shared/utils/roles'
import {
  ESTADOS_COMPRA,
  REPORTE_TABS,
  buildResumenCards,
  formatDate,
  formatDateTime,
  getApiErrorMessage,
  getEstadoTone,
  getMaxValue,
  localDateTimeToIso,
  numberValue
} from '@/shared/utils/reportes'

const emptyResumen = {
  totalVentas: 0,
  cantidadVentas: 0,
  ticketPromedio: 0,
  productosConStockBajo: 0,
  alertasPendientes: 0,
  ordenesCompraAbiertas: 0,
  reposicionesAbiertas: 0
}

function BarList({ data, labelKey, valueKey, valueFormatter = (value) => value, emptyMessage = 'No hay datos para graficar.' }) {
  const maxValue = getMaxValue(data, valueKey)

  if (data.length === 0) {
    return (
      <div className="rounded-2xl border border-dashed border-slate-200 bg-slate-50 p-6 text-center text-sm text-slate-500">
        {emptyMessage}
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {data.map((item, index) => {
        const value = numberValue(item[valueKey])
        const width = Math.max(6, Math.round((value / maxValue) * 100))
        const key = `${item[labelKey]}-${index}`

        return (
          <div key={key} className="space-y-1.5">
            <div className="flex items-center justify-between gap-3 text-sm">
              <span className="truncate font-semibold text-slate-700">{item[labelKey]}</span>
              <span className="shrink-0 font-bold text-slate-950">{valueFormatter(value)}</span>
            </div>
            <div className="h-2.5 overflow-hidden rounded-full bg-slate-100">
              <div className="h-full rounded-full bg-slate-900" style={{ width: `${width}%` }} />
            </div>
          </div>
        )
      })}
    </div>
  )
}

function sanitizeLimitInput(value, min, max) {
  if (value === '') return ''
  const number = Number(value)
  if (!Number.isFinite(number)) return ''
  if (number < min) return String(min)
  if (number > max) return String(max)
  return String(Math.floor(number))
}

function Tabs({ activeTab, onChange, canViewCompras, canViewReposiciones }) {
  const tabs = [
    { id: REPORTE_TABS.RESUMEN, label: 'Resumen' },
    { id: REPORTE_TABS.VENTAS, label: 'Ventas por fecha' },
    { id: REPORTE_TABS.PRODUCTOS, label: 'Más vendidos' },
    { id: REPORTE_TABS.STOCK, label: 'Stock bajo' },
    { id: REPORTE_TABS.KARDEX, label: 'Kardex' },
    canViewCompras ? { id: REPORTE_TABS.COMPRAS, label: 'Compras' } : null,
    canViewReposiciones ? { id: REPORTE_TABS.REPOSICIONES, label: 'Reposiciones' } : null
  ].filter(Boolean)

  return (
    <div className="overflow-x-auto rounded-2xl border border-slate-200 bg-white p-1 shadow-sm">
      <div className="flex min-w-max gap-1">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => onChange(tab.id)}
            className={`rounded-xl px-4 py-2 text-sm font-bold transition ${
              activeTab === tab.id
                ? 'bg-slate-900 text-white shadow-sm'
                : 'text-slate-600 hover:bg-slate-100 hover:text-slate-950'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>
    </div>
  )
}

export default function ReportesPage() {
  const { usuario } = useAuth()
  const role = usuario?.rol
  const hasGlobalView = canSeeAllLocations(role)
  const canViewCompras = [ROLES.ADMIN, ROLES.SUPERVISOR_ALMACEN].includes(role)
  const canViewReposiciones = [ROLES.ADMIN, ROLES.SUPERVISOR_ALMACEN, ROLES.SUPERVISOR_SUCURSAL].includes(role)

  const [activeTab, setActiveTab] = useState(REPORTE_TABS.RESUMEN)
  const [ubicaciones, setUbicaciones] = useState([])
  const [productos, setProductos] = useState([])
  const [resumen, setResumen] = useState(emptyResumen)
  const [ventasPorFecha, setVentasPorFecha] = useState([])
  const [productosVendidos, setProductosVendidos] = useState([])
  const [stockBajo, setStockBajo] = useState([])
  const [kardex, setKardex] = useState([])
  const [compras, setCompras] = useState([])
  const [reposicionesEstado, setReposicionesEstado] = useState([])
  const [filters, setFilters] = useState({
    idUbicacion: '',
    idProducto: '',
    estadoCompra: '',
    desde: '',
    hasta: '',
    limiteProductos: 10,
    limiteKardex: 200,
    limiteCompras: 100
  })
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(false)
  const [error, setError] = useState('')
  const [lastUpdated, setLastUpdated] = useState(null)

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

  const reportFilters = useMemo(() => ({
    idUbicacion: filters.idUbicacion || undefined,
    idProducto: filters.idProducto || undefined,
    estadoCompra: filters.estadoCompra || undefined,
    desde: localDateTimeToIso(filters.desde),
    hasta: localDateTimeToIso(filters.hasta),
    limiteProductos: Number(filters.limiteProductos || 10),
    limiteKardex: Number(filters.limiteKardex || 200),
    limiteCompras: Number(filters.limiteCompras || 100)
  }), [filters])

  const resumenCards = useMemo(() => buildResumenCards(resumen), [resumen])

  async function loadCatalogos() {
    const requests = [listarProductos({ incluirInactivos: false })]

    if (hasGlobalView) {
      requests.push(listarUbicaciones({ incluirInactivas: false }))
    }

    const [productosData, ubicacionesData = []] = await Promise.all(requests)
    setProductos(productosData)
    setUbicaciones(ubicacionesData)
  }

  async function loadReportes(filtersToUse = reportFilters) {
    setError('')

    try {
      const common = {
        idUbicacion: filtersToUse.idUbicacion,
        desde: filtersToUse.desde,
        hasta: filtersToUse.hasta
      }

      const baseRequests = [
        obtenerResumenReporte(common),
        listarVentasPorFecha(common),
        listarProductosMasVendidos({ ...common, limite: filtersToUse.limiteProductos }),
        listarStockBajoReporte({ idUbicacion: filtersToUse.idUbicacion }),
        listarKardexReporte({
          ...common,
          idProducto: filtersToUse.idProducto,
          limite: filtersToUse.limiteKardex
        })
      ]

      const optionalRequests = []

      if (canViewCompras) {
        optionalRequests.push(
          listarComprasReporte({
            ...common,
            estado: filtersToUse.estadoCompra,
            limite: filtersToUse.limiteCompras
          })
        )
      }

      if (canViewReposiciones) {
        optionalRequests.push(
          listarReposicionesPorEstado({ idUbicacionDestino: filtersToUse.idUbicacion })
        )
      }

      const [
        resumenData,
        ventasData,
        productosData,
        stockData,
        kardexData,
        ...optionalData
      ] = await Promise.all([...baseRequests, ...optionalRequests])

      setResumen(resumenData)
      setVentasPorFecha(ventasData)
      setProductosVendidos(productosData)
      setStockBajo(stockData)
      setKardex(kardexData)

      let optionalIndex = 0
      if (canViewCompras) {
        setCompras(optionalData[optionalIndex] || [])
        optionalIndex += 1
      } else {
        setCompras([])
      }

      if (canViewReposiciones) {
        setReposicionesEstado(optionalData[optionalIndex] || [])
      } else {
        setReposicionesEstado([])
      }

      setLastUpdated(new Date())
    } catch (err) {
      setError(getApiErrorMessage(err, 'No se pudieron cargar los reportes'))
    }
  }

  async function loadInitialData() {
    setLoading(true)
    try {
      await loadCatalogos()
      await loadReportes(reportFilters)
    } catch (err) {
      setError(getApiErrorMessage(err, 'No se pudo iniciar la pantalla de reportes'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadInitialData()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  function updateFilter(field, value) {
    let nextValue = value

    if (field === 'limiteProductos') nextValue = sanitizeLimitInput(value, 1, 100)
    if (field === 'limiteKardex') nextValue = sanitizeLimitInput(value, 1, 1000)
    if (field === 'limiteCompras') nextValue = sanitizeLimitInput(value, 1, 500)

    setFilters((current) => ({ ...current, [field]: nextValue }))
  }

  async function handleApplyFilters(event) {
    event.preventDefault()
    setActionLoading(true)
    try {
      await loadReportes(reportFilters)
    } finally {
      setActionLoading(false)
    }
  }

  async function handleClearFilters() {
    const cleanFilters = {
      idUbicacion: '',
      idProducto: '',
      estadoCompra: '',
      desde: '',
      hasta: '',
      limiteProductos: 10,
      limiteKardex: 200,
      limiteCompras: 100
    }

    setFilters(cleanFilters)
    setActionLoading(true)
    try {
      await loadReportes({
        idUbicacion: undefined,
        idProducto: undefined,
        estadoCompra: undefined,
        desde: undefined,
        hasta: undefined,
        limiteProductos: 10,
        limiteKardex: 200,
        limiteCompras: 100
      })
    } finally {
      setActionLoading(false)
    }
  }

  const ventaColumns = [
    { key: 'fecha', header: 'Fecha', render: (row) => formatDate(row.fecha) },
    { key: 'cantidadVentas', header: 'Ventas' },
    { key: 'subtotalVenta', header: 'Subtotal', render: (row) => formatMoney(row.subtotalVenta) },
    { key: 'totalIgv', header: 'IGV', render: (row) => formatMoney(row.totalIgv) },
    { key: 'totalVenta', header: 'Total', render: (row) => formatMoney(row.totalVenta) }
  ]

  const productoColumns = [
    { key: 'idProducto', header: 'ID' },
    { key: 'codigoBarras', header: 'Código' },
    { key: 'nombreProducto', header: 'Producto' },
    { key: 'cantidadVendida', header: 'Cantidad' },
    { key: 'totalVendido', header: 'Total', render: (row) => formatMoney(row.totalVendido) }
  ]

  const stockColumns = [
    { key: 'idInventario', header: 'ID' },
    { key: 'ubicacion', header: 'Ubicación' },
    { key: 'codigoBarras', header: 'Código' },
    { key: 'producto', header: 'Producto' },
    { key: 'stockDisponible', header: 'Stock' },
    { key: 'stockMinimo', header: 'Mínimo' },
    {
      key: 'estadoStock',
      header: 'Estado',
      render: (row) => <Badge tone={getEstadoTone(row.estadoStock)}>{row.estadoStock}</Badge>
    }
  ]

  const kardexColumns = [
    { key: 'fechaHora', header: 'Fecha', render: (row) => formatDateTime(row.fechaHora) },
    { key: 'ubicacion', header: 'Ubicación' },
    { key: 'producto', header: 'Producto' },
    {
      key: 'tipoMovimiento',
      header: 'Tipo',
      render: (row) => <Badge tone={getEstadoTone(row.tipoMovimiento)}>{row.tipoMovimiento}</Badge>
    },
    { key: 'motivoMovimiento', header: 'Motivo' },
    { key: 'cantidad', header: 'Cantidad' },
    { key: 'usuario', header: 'Usuario' },
    { key: 'referencia', header: 'Referencia', render: (row) => row.tipoReferencia ? `${row.tipoReferencia} #${row.idReferencia}` : '-' }
  ]

  const comprasColumns = [
    { key: 'idOrdenCompra', header: 'ID' },
    { key: 'proveedor', header: 'Proveedor' },
    { key: 'ubicacionDestino', header: 'Destino' },
    {
      key: 'estado',
      header: 'Estado',
      render: (row) => <Badge tone={getEstadoTone(row.estado)}>{row.estado}</Badge>
    },
    { key: 'fechaPedido', header: 'Pedido', render: (row) => formatDateTime(row.fechaPedido) },
    { key: 'fechaRecepcion', header: 'Recepción', render: (row) => formatDateTime(row.fechaRecepcion) },
    { key: 'totalCompra', header: 'Total', render: (row) => formatMoney(row.totalCompra) }
  ]

  const reposicionColumns = [
    {
      key: 'estado',
      header: 'Estado',
      render: (row) => <Badge tone={getEstadoTone(row.estado)}>{row.estado}</Badge>
    },
    { key: 'cantidad', header: 'Cantidad' }
  ]

  if (loading) return <Loader message="Cargando reportes..." />

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Análisis"
        title="Reportes"
        description="Consulta indicadores del sistema: ventas, productos más vendidos, stock bajo, kardex, compras y reposiciones."
        actions={
          lastUpdated && (
            <span className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-500">
              Actualizado: {formatDateTime(lastUpdated.toISOString())}
            </span>
          )
        }
      />

      {error && <Alert tone="error">{error}</Alert>}

      <form onSubmit={handleApplyFilters} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <Select
            label="Ubicación"
            value={filters.idUbicacion}
            onChange={(event) => updateFilter('idUbicacion', event.target.value)}
            disabled={!hasGlobalView}
          >
            <option value="">{hasGlobalView ? 'Todas las ubicaciones' : usuario?.ubicacion || 'Mi ubicación'}</option>
            {ubicacionOptions.map((ubicacion) => (
              <option key={ubicacion.idUbicacion} value={ubicacion.idUbicacion}>
                {ubicacion.nombreUbicacion}
              </option>
            ))}
          </Select>

          <Input
            label="Desde"
            type="datetime-local"
            value={filters.desde}
            onChange={(event) => updateFilter('desde', event.target.value)}
          />

          <Input
            label="Hasta"
            type="datetime-local"
            value={filters.hasta}
            onChange={(event) => updateFilter('hasta', event.target.value)}
          />

          <Select
            label="Producto para Kardex"
            value={filters.idProducto}
            onChange={(event) => updateFilter('idProducto', event.target.value)}
          >
            <option value="">Todos los productos</option>
            {productos.map((producto) => (
              <option key={producto.idProducto} value={producto.idProducto}>
                {producto.nombreProducto}
              </option>
            ))}
          </Select>
        </div>

        <div className="mt-4 grid gap-4 md:grid-cols-3 xl:grid-cols-4">
          <Input
            label="Límite productos vendidos"
            type="number"
            min="1"
            max="100"
            value={filters.limiteProductos}
            onChange={(event) => updateFilter('limiteProductos', event.target.value)}
          />

          <Input
            label="Límite kardex"
            type="number"
            min="1"
            max="1000"
            value={filters.limiteKardex}
            onChange={(event) => updateFilter('limiteKardex', event.target.value)}
          />

          {canViewCompras && (
            <Select
              label="Estado de compra"
              value={filters.estadoCompra}
              onChange={(event) => updateFilter('estadoCompra', event.target.value)}
            >
              <option value="">Todos</option>
              {ESTADOS_COMPRA.map((estado) => (
                <option key={estado} value={estado}>{estado}</option>
              ))}
            </Select>
          )}

          {canViewCompras && (
            <Input
              label="Límite compras"
              type="number"
              min="1"
              max="500"
              value={filters.limiteCompras}
              onChange={(event) => updateFilter('limiteCompras', event.target.value)}
            />
          )}
        </div>

        <div className="mt-5 flex flex-wrap gap-2">
          <Button type="submit" disabled={actionLoading}>{actionLoading ? 'Cargando...' : 'Aplicar filtros'}</Button>
          <Button type="button" variant="secondary" onClick={handleClearFilters} disabled={actionLoading}>Limpiar</Button>
        </div>
      </form>

      <Tabs
        activeTab={activeTab}
        onChange={setActiveTab}
        canViewCompras={canViewCompras}
        canViewReposiciones={canViewReposiciones}
      />

      {activeTab === REPORTE_TABS.RESUMEN && (
        <section className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {resumenCards.map((card) => (
              <Card
                key={card.title}
                title={card.title}
                value={card.money ? formatMoney(card.value) : card.value ?? 0}
                description={card.description}
              />
            ))}
          </div>
        </section>
      )}

      {activeTab === REPORTE_TABS.VENTAS && (
        <section className="grid gap-4 xl:grid-cols-[0.9fr_1.1fr]">
          <Card title="Gráfico de ventas" description="Total vendido por fecha">
            <div className="mt-4">
              <BarList
                data={ventasPorFecha.map((item) => ({ ...item, fechaLabel: formatDate(item.fecha) }))}
                labelKey="fechaLabel"
                valueKey="totalVenta"
                valueFormatter={formatMoney}
                emptyMessage="Aún no hay ventas para el rango seleccionado."
              />
            </div>
          </Card>
          <div>
            <Table columns={ventaColumns} data={ventasPorFecha} keyField="fecha" emptyMessage="No hay ventas para mostrar." />
          </div>
        </section>
      )}

      {activeTab === REPORTE_TABS.PRODUCTOS && (
        <section className="grid gap-4 xl:grid-cols-[0.9fr_1.1fr]">
          <Card title="Productos más vendidos" description="Ranking por cantidad vendida">
            <div className="mt-4">
              <BarList
                data={productosVendidos}
                labelKey="nombreProducto"
                valueKey="cantidadVendida"
                emptyMessage="Aún no hay productos vendidos."
              />
            </div>
          </Card>
          <div>
            <Table columns={productoColumns} data={productosVendidos} keyField="idProducto" emptyMessage="No hay productos vendidos para mostrar." />
          </div>
        </section>
      )}

      {activeTab === REPORTE_TABS.STOCK && (
        <section className="space-y-4">
          <Card title="Stock bajo" value={stockBajo.length} description="Productos con stock disponible menor o igual al stock mínimo" />
          <Table columns={stockColumns} data={stockBajo} keyField="idInventario" emptyMessage="No hay productos con stock bajo." />
        </section>
      )}

      {activeTab === REPORTE_TABS.KARDEX && (
        <section className="space-y-4">
          <Card title="Kardex" value={kardex.length} description="Últimos movimientos según los filtros seleccionados" />
          <Table columns={kardexColumns} data={kardex} keyField="idMovimiento" emptyMessage="No hay movimientos para mostrar." />
        </section>
      )}

      {activeTab === REPORTE_TABS.COMPRAS && canViewCompras && (
        <section className="space-y-4">
          <Card
            title="Compras reportadas"
            value={formatMoney(compras.reduce((sum, compra) => sum + numberValue(compra.totalCompra), 0))}
            description={`${compras.length} orden(es) encontradas`}
          />
          <Table columns={comprasColumns} data={compras} keyField="idOrdenCompra" emptyMessage="No hay compras para mostrar." />
        </section>
      )}

      {activeTab === REPORTE_TABS.REPOSICIONES && canViewReposiciones && (
        <section className="grid gap-4 xl:grid-cols-[0.9fr_1.1fr]">
          <Card title="Reposiciones por estado" description="Cantidad de solicitudes agrupadas por estado">
            <div className="mt-4">
              <BarList
                data={reposicionesEstado}
                labelKey="estado"
                valueKey="cantidad"
                emptyMessage="No hay reposiciones para graficar."
              />
            </div>
          </Card>
          <div>
            <Table columns={reposicionColumns} data={reposicionesEstado} keyField="estado" emptyMessage="No hay reposiciones para mostrar." />
          </div>
        </section>
      )}
    </div>
  )
}
