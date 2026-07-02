import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { listarInventario, listarMovimientos } from '@/shared/api/inventarioApi'
import { listarReposiciones } from '@/shared/api/reposicionApi'
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
import { countCriticalStock, countLowStock, formatDateTime, stockLabel, stockTone, sumStock } from '@/shared/utils/roleViews'

export default function InventarioPage() {
  const { usuario } = useAuth()
  const [inventario, setInventario] = useState([])
  const [movimientos, setMovimientos] = useState([])
  const [reposiciones, setReposiciones] = useState([])
  const [search, setSearch] = useState('')
  const [estado, setEstado] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let mounted = true

    async function loadData() {
      setError('')
      setLoading(true)
      try {
        const idUbicacion = usuario?.idUbicacion
        const [inventarioData, movimientosData, reposicionesData] = await Promise.all([
          listarInventario({ idUbicacion }),
          listarMovimientos({ idUbicacion, limite: 80 }),
          listarReposiciones({ idUbicacionDestino: idUbicacion, limite: 80 })
        ])
        if (!mounted) return
        setInventario(inventarioData)
        setMovimientos(movimientosData)
        setReposiciones(reposicionesData)
      } catch (err) {
        if (mounted) setError(err.message || 'No se pudo cargar el inventario de la sucursal')
      } finally {
        if (mounted) setLoading(false)
      }
    }

    loadData()
    return () => { mounted = false }
  }, [usuario?.idUbicacion])

  const filteredInventario = useMemo(() => {
    const term = search.trim().toLowerCase()
    return inventario.filter((item) => {
      const matchTerm = !term || [item.producto, item.codigoBarras, item.categoria]
        .some((value) => String(value || '').toLowerCase().includes(term))
      const label = stockLabel(item)
      const matchEstado = !estado || label === estado
      return matchTerm && matchEstado
    })
  }, [inventario, search, estado])

  const resumen = useMemo(() => ({
    totalProductos: inventario.length,
    stockCritico: countCriticalStock(inventario),
    stockBajo: countLowStock(inventario),
    unidades: sumStock(inventario),
    solicitudesAbiertas: reposiciones.filter((item) => !['RECIBIDA', 'RECHAZADA', 'CANCELADA'].includes(item.estado)).length,
    recepcionesPendientes: reposiciones.filter((item) => item.estado === 'EN_TRANSITO').length
  }), [inventario, reposiciones])

  const inventarioColumns = [
    { key: 'codigoBarras', header: 'Código' },
    { key: 'producto', header: 'Producto', render: (row) => <span className="font-semibold text-slate-950">{row.producto}</span> },
    { key: 'categoria', header: 'Categoría', render: (row) => row.categoria || 'General' },
    { key: 'stockDisponible', header: 'Stock actual', render: (row) => <span className="font-bold text-slate-950">{row.stockDisponible}</span> },
    { key: 'stockMinimo', header: 'Stock mínimo' },
    { key: 'estado', header: 'Estado', render: (row) => <Badge tone={stockTone(row)}>{stockLabel(row)}</Badge> },
    { key: 'precio', header: 'Precio', render: (row) => row.precioVenta ? `S/ ${Number(row.precioVenta).toFixed(2)}` : '-' }
  ]

  const movimientoColumns = [
    { key: 'fechaHora', header: 'Fecha', render: (row) => formatDateTime(row.fechaHora) },
    { key: 'producto', header: 'Producto' },
    { key: 'tipoMovimiento', header: 'Tipo', render: (row) => <Badge tone={row.tipoMovimiento === 'INGRESO' ? 'green' : 'red'}>{row.tipoMovimiento === 'INGRESO' ? 'Entrada' : 'Salida'}</Badge> },
    { key: 'motivoMovimiento', header: 'Motivo' },
    { key: 'cantidad', header: 'Cantidad' }
  ]

  if (loading) return <Loader message="Cargando inventario de sucursal..." />

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Inventario"
        title={usuario?.ubicacion || 'Mi sucursal'}
        description="Consulta el inventario de la sucursal asignada, filtra productos y detecta stock mínimo o crítico."
        action={(
          <div className="flex flex-wrap gap-2">
            <Button as={Link} to="/solicitudes-reposicion">Nueva solicitud</Button>
            <Button as={Link} to="/alertas-stock" variant="secondary">Ver alertas</Button>
          </div>
        )}
      />

      {error && <Alert tone="error">{error}</Alert>}

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-6">
        <Card title="Productos" value={resumen.totalProductos} description="En mi sucursal" />
        <Card title="Stock crítico" value={resumen.stockCritico} description="Agotados" />
        <Card title="Stock bajo" value={resumen.stockBajo} description="En mínimo" />
        <Card title="Unidades" value={resumen.unidades} description="Stock acumulado" />
        <Card title="Solicitudes abiertas" value={resumen.solicitudesAbiertas} description="Reposición en proceso" />
        <Card title="Por recibir" value={resumen.recepcionesPendientes} description="En tránsito" />
      </section>

      <Card>
        <div className="grid gap-3 md:grid-cols-2">
          <Input label="Buscar producto" placeholder="Nombre, categoría o código" value={search} onChange={(event) => setSearch(event.target.value)} />
          <Select label="Estado" value={estado} onChange={(event) => setEstado(event.target.value)}>
            <option value="">Todos</option>
            <option value="Disponible">Disponible</option>
            <option value="Bajo stock">Bajo stock</option>
            <option value="Agotado">Agotado</option>
          </Select>
        </div>
      </Card>

      <Table columns={inventarioColumns} data={filteredInventario} keyField="idInventario" emptyMessage="No hay inventario para tu sucursal con estos filtros." />

      <section className="space-y-3">
        <div className="flex items-center justify-between gap-3">
          <h2 className="text-lg font-bold text-slate-950">Movimientos recientes</h2>
          <Button as={Link} to="/movimientos" variant="secondary">Ver todos</Button>
        </div>
        <Table columns={movimientoColumns} data={movimientos.slice(0, 8)} keyField="idMovimiento" emptyMessage="No hay movimientos recientes." />
      </section>
    </div>
  )
}
