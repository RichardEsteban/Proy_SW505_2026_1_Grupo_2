import { useEffect, useMemo, useState } from 'react'
import { listarInventario, listarMovimientos } from '@/shared/api/inventarioApi'
import Alert from '@/shared/components/Alert'
import Badge from '@/shared/components/Badge'
import Card from '@/shared/components/Card'
import Input from '@/shared/components/Input'
import Loader from '@/shared/components/Loader'
import PageHeader from '@/shared/components/PageHeader'
import Table from '@/shared/components/Table'
import { formatMoney } from '@/shared/utils/formatMoney'
import {
  countCriticalStock,
  countLowStock,
  formatDateTime,
  isCentralWarehouse,
  stockLabel,
  stockTone,
  sumStock
} from '@/shared/utils/roleViews'

export default function InventarioPage() {
  const [inventario, setInventario] = useState([])
  const [movimientos, setMovimientos] = useState([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let mounted = true

    async function loadData() {
      try {
        const [inventarioData, movimientosData] = await Promise.all([
          listarInventario(),
          listarMovimientos({ limite: 20 })
        ])
        if (!mounted) return
        setInventario(inventarioData.filter(isCentralWarehouse))
        setMovimientos(movimientosData.filter(isCentralWarehouse).slice(0, 10))
      } catch (err) {
        if (mounted) setError(err.message || 'No se pudo cargar el almacén central')
      } finally {
        if (mounted) setLoading(false)
      }
    }

    loadData()
    return () => { mounted = false }
  }, [])

  const filteredInventario = useMemo(() => {
    const term = search.trim().toLowerCase()
    if (!term) return inventario
    return inventario.filter((item) => (
      String(item.idProducto).includes(term) ||
      String(item.codigoBarras || '').toLowerCase().includes(term) ||
      String(item.producto || '').toLowerCase().includes(term) ||
      String(item.ubicacion || '').toLowerCase().includes(term)
    ))
  }, [inventario, search])

  const resumen = useMemo(() => ({
    totalProductos: inventario.length,
    stockCritico: countCriticalStock(inventario),
    stockBajo: countLowStock(inventario),
    stockNormal: inventario.filter((item) => stockLabel(item) === 'Disponible').length,
    unidadesTotales: sumStock(inventario),
    valorTotal: inventario.reduce((total, item) => total + Number(item.stockDisponible || 0) * Number(item.precioVenta || item.precio || 0), 0)
  }), [inventario])

  const columns = [
    { key: 'codigoBarras', header: 'Código', render: (row) => <span className="font-semibold text-slate-900">{row.codigoBarras}</span> },
    { key: 'producto', header: 'Producto', render: (row) => <div><p className="font-semibold text-slate-950">{row.producto}</p><p className="text-xs text-slate-500">Categoría: pendiente de enlazar en BD</p></div> },
    { key: 'stockDisponible', header: 'Stock actual', render: (row) => <span className="text-lg font-black text-slate-950">{row.stockDisponible}</span> },
    { key: 'stockMinimo', header: 'Stock mínimo' },
    { key: 'ubicacion', header: 'Ubicación' },
    { key: 'estado', header: 'Estado', render: (row) => <Badge tone={stockTone(row)}>{stockLabel(row)}</Badge> },
    { key: 'categoria', header: 'Categoría', render: (row) => row.categoria || 'Sin categoría' }
  ]

  const movementColumns = [
    { key: 'fechaHora', header: 'Fecha', render: (row) => formatDateTime(row.fechaHora) },
    { key: 'producto', header: 'Producto' },
    { key: 'tipoMovimiento', header: 'Tipo', render: (row) => <Badge tone={row.tipoMovimiento === 'INGRESO' ? 'green' : 'red'}>{row.tipoMovimiento === 'INGRESO' ? 'Entrada' : 'Salida'}</Badge> },
    { key: 'motivoMovimiento', header: 'Motivo' },
    { key: 'cantidad', header: 'Cantidad', render: (row) => <span className="font-bold text-slate-950">{row.cantidad}</span> }
  ]

  if (loading) return <Loader message="Cargando almacén central..." />

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Inventario"
        title="Inventario del almacén central"
        description="Consulta productos, stock disponible, stock mínimo, estado y movimientos recientes del almacén central."
      />

      {error && <Alert tone="error">{error}</Alert>}

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-6">
        <Card title="Total productos" value={resumen.totalProductos} description="Registros visibles" />
        <Card title="Stock crítico" value={resumen.stockCritico} description="Agotados" />
        <Card title="Stock bajo" value={resumen.stockBajo} description="En mínimo" />
        <Card title="Stock normal" value={resumen.stockNormal} description="Disponibles" />
        <Card title="Unidades totales" value={resumen.unidadesTotales} description="Stock acumulado" />
        <Card title="Valor total" value={formatMoney(resumen.valorTotal)} description="Estimado por precio venta" />
      </section>

      <Card>
        <Input
          label="Buscar producto"
          placeholder="Nombre, código, ID o ubicación"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
        />
      </Card>

      <Table columns={columns} data={filteredInventario} keyField="idInventario" emptyMessage="No hay productos registrados en el almacén central." />

      <section className="space-y-3">
        <h2 className="text-lg font-bold text-slate-950">Movimientos recientes</h2>
        <Table columns={movementColumns} data={movimientos} keyField="idMovimiento" emptyMessage="No hay movimientos recientes en almacén central." />
      </section>
    </div>
  )
}
