import { useEffect, useMemo, useState } from 'react'
import { listarInventario, listarMovimientos } from '@/shared/api/inventarioApi'
import { listarReposiciones } from '@/shared/api/reposicionApi'
import { listarUbicaciones } from '@/shared/api/ubicacionApi'
import Alert from '@/shared/components/Alert'
import Badge from '@/shared/components/Badge'
import Button from '@/shared/components/Button'
import Card from '@/shared/components/Card'
import Input from '@/shared/components/Input'
import Loader from '@/shared/components/Loader'
import PageHeader from '@/shared/components/PageHeader'
import Table from '@/shared/components/Table'
import { formatMoney } from '@/shared/utils/formatMoney'
import { countCriticalStock, countLowStock, formatDateTime, isCentralWarehouse, stockLabel, stockTone, sumStock } from '@/shared/utils/roleViews'

function getSucursalFallbackName(index) {
  return ['Sucursal Norte', 'Sucursal Sur', 'Sucursal Centro', 'Sucursal Este'][index] || `Sucursal ${index + 1}`
}

export default function SucursalesPage() {
  const [ubicaciones, setUbicaciones] = useState([])
  const [inventario, setInventario] = useState([])
  const [movimientos, setMovimientos] = useState([])
  const [reposiciones, setReposiciones] = useState([])
  const [selectedSucursal, setSelectedSucursal] = useState(null)
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let mounted = true

    async function loadData() {
      try {
        const [ubicacionesData, inventarioData, movimientosData, reposicionesData] = await Promise.all([
          listarUbicaciones({ incluirInactivas: false }),
          listarInventario(),
          listarMovimientos({ limite: 100 }),
          listarReposiciones({ limite: 100 })
        ])
        if (!mounted) return
        const sucursales = ubicacionesData.filter((ubicacion) => !isCentralWarehouse(ubicacion))
        setUbicaciones(sucursales)
        setSelectedSucursal(sucursales[0] || null)
        setInventario(inventarioData)
        setMovimientos(movimientosData)
        setReposiciones(reposicionesData)
      } catch (err) {
        if (mounted) setError(err.message || 'No se pudieron cargar las sucursales')
      } finally {
        if (mounted) setLoading(false)
      }
    }

    loadData()
    return () => { mounted = false }
  }, [])

  const resumenGeneral = useMemo(() => {
    const inventarioSucursales = inventario.filter((item) => !isCentralWarehouse(item))
    return {
      totalSucursales: ubicaciones.length,
      totalProductos: inventarioSucursales.length,
      stockBajo: countLowStock(inventarioSucursales) + countCriticalStock(inventarioSucursales),
      valorTotal: inventarioSucursales.reduce((total, item) => total + Number(item.stockDisponible || 0) * Number(item.precioVenta || item.precio || 0), 0)
    }
  }, [ubicaciones, inventario])

  const sucursalInventario = useMemo(() => {
    if (!selectedSucursal) return []
    const term = search.trim().toLowerCase()
    return inventario
      .filter((item) => Number(item.idUbicacion) === Number(selectedSucursal.idUbicacion))
      .filter((item) => !term || String(item.producto || '').toLowerCase().includes(term) || String(item.codigoBarras || '').toLowerCase().includes(term))
  }, [inventario, selectedSucursal, search])

  const sucursalMovimientos = useMemo(() => {
    if (!selectedSucursal) return []
    return movimientos.filter((item) => Number(item.idUbicacion) === Number(selectedSucursal.idUbicacion)).slice(0, 10)
  }, [movimientos, selectedSucursal])

  const sucursalReposiciones = useMemo(() => {
    if (!selectedSucursal) return []
    return reposiciones.filter((item) => Number(item.idUbicacionDestino) === Number(selectedSucursal.idUbicacion)).slice(0, 10)
  }, [reposiciones, selectedSucursal])

  const resumenSucursal = useMemo(() => ({
    totalProductos: sucursalInventario.length,
    stockCritico: countCriticalStock(sucursalInventario),
    stockBajo: countLowStock(sucursalInventario),
    solicitudes: sucursalReposiciones.length,
    unidadesTotales: sumStock(sucursalInventario),
    precioTotal: sucursalInventario.reduce((total, item) => total + Number(item.stockDisponible || 0) * Number(item.precioVenta || item.precio || 0), 0)
  }), [sucursalInventario, sucursalReposiciones])

  const inventarioColumns = [
    { key: 'codigoBarras', header: 'Código' },
    { key: 'producto', header: 'Producto', render: (row) => <span className="font-semibold text-slate-950">{row.producto}</span> },
    { key: 'stockDisponible', header: 'Stock' },
    { key: 'stockMinimo', header: 'Mínimo' },
    { key: 'estado', header: 'Estado', render: (row) => <Badge tone={stockTone(row)}>{stockLabel(row)}</Badge> }
  ]

  const movimientoColumns = [
    { key: 'fechaHora', header: 'Fecha', render: (row) => formatDateTime(row.fechaHora) },
    { key: 'producto', header: 'Producto' },
    { key: 'tipoMovimiento', header: 'Tipo', render: (row) => <Badge tone={row.tipoMovimiento === 'INGRESO' ? 'green' : 'red'}>{row.tipoMovimiento}</Badge> },
    { key: 'cantidad', header: 'Cantidad' }
  ]

  const solicitudColumns = [
    { key: 'idSolicitud', header: 'N°', render: (row) => <span className="font-semibold text-slate-950">TRANS-{String(row.idSolicitud).padStart(4, '0')}</span> },
    { key: 'estado', header: 'Estado', render: (row) => <Badge tone={row.estado === 'RECHAZADA' ? 'red' : row.estado === 'RECIBIDA' ? 'green' : 'amber'}>{row.estado}</Badge> },
    { key: 'fechaSolicitud', header: 'Fecha', render: (row) => formatDateTime(row.fechaSolicitud) },
    { key: 'origen', header: 'Origen', render: (row) => row.ubicacionOrigen || row.origen || '-' }
  ]

  if (loading) return <Loader message="Cargando sucursales..." />

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Sucursales"
        title="Control de sucursales"
        description="Visualiza cada sucursal, su dirección, responsables pendientes de configurar, productos, stock bajo, movimientos y solicitudes realizadas."
      />

      {error && <Alert tone="error">{error}</Alert>}

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Card title="Total sucursales" value={resumenGeneral.totalSucursales} description="Activas" />
        <Card title="Productos en sucursales" value={resumenGeneral.totalProductos} description="Registros de inventario" />
        <Card title="Stock bajo/crítico" value={resumenGeneral.stockBajo} description="Productos a reponer" />
        <Card title="Valor total" value={formatMoney(resumenGeneral.valorTotal)} description="Estimado por precio venta" />
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {ubicaciones.map((sucursal, index) => (
          <button
            key={sucursal.idUbicacion}
            type="button"
            onClick={() => setSelectedSucursal(sucursal)}
            className={`rounded-2xl border p-5 text-left shadow-sm transition ${selectedSucursal?.idUbicacion === sucursal.idUbicacion ? 'border-slate-900 bg-slate-900 text-white' : 'border-slate-200 bg-white hover:border-slate-400'}`}
          >
            <p className="text-xs font-bold uppercase tracking-wide opacity-70">{getSucursalFallbackName(index)}</p>
            <h3 className="mt-2 text-lg font-black">{sucursal.nombreUbicacion}</h3>
            <p className="mt-2 text-sm opacity-80">{sucursal.direccion}</p>
            <p className="mt-3 text-xs opacity-70">Responsable y teléfono: pendiente de registrar</p>
          </button>
        ))}
      </section>

      {selectedSucursal && (
        <section className="space-y-5">
          <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex flex-col justify-between gap-3 md:flex-row md:items-center">
              <div>
                <p className="text-sm font-semibold text-slate-500">Vista de sucursal</p>
                <h2 className="text-2xl font-black text-slate-950">{selectedSucursal.nombreUbicacion}</h2>
                <p className="text-sm text-slate-500">{selectedSucursal.direccion}</p>
              </div>
              <Badge tone="green">{selectedSucursal.tipoUbicacion}</Badge>
            </div>
          </div>

          <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-6">
            <Card title="Total productos" value={resumenSucursal.totalProductos} description="En esta sucursal" />
            <Card title="Stock crítico" value={resumenSucursal.stockCritico} description="Agotados" />
            <Card title="Stock bajo" value={resumenSucursal.stockBajo} description="En mínimo" />
            <Card title="Solicitudes" value={resumenSucursal.solicitudes} description="Últimas visibles" />
            <Card title="Unidades" value={resumenSucursal.unidadesTotales} description="Stock acumulado" />
            <Card title="Precio total" value={formatMoney(resumenSucursal.precioTotal)} description="Estimado" />
          </section>

          <Card>
            <Input label="Buscar en inventario" placeholder="Producto o código" value={search} onChange={(event) => setSearch(event.target.value)} />
          </Card>

          <Table columns={inventarioColumns} data={sucursalInventario} keyField="idInventario" emptyMessage="Esta sucursal no tiene inventario con los filtros actuales." />

          <section className="grid gap-5 xl:grid-cols-2">
            <div className="space-y-3">
              <h3 className="font-bold text-slate-950">Movimientos recientes</h3>
              <Table columns={movimientoColumns} data={sucursalMovimientos} keyField="idMovimiento" emptyMessage="No hay movimientos recientes." />
            </div>
            <div className="space-y-3">
              <h3 className="font-bold text-slate-950">Solicitudes realizadas</h3>
              <Table columns={solicitudColumns} data={sucursalReposiciones} keyField="idSolicitud" emptyMessage="No hay solicitudes visibles." />
            </div>
          </section>
        </section>
      )}
    </div>
  )
}
