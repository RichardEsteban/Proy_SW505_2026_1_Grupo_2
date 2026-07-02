import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { listarInventario, listarMovimientos } from '@/shared/api/inventarioApi'
import { listarReposiciones } from '@/shared/api/reposicionApi'
import { listarOrdenesCompra } from '@/shared/api/ordenCompraApi'
import Alert from '@/shared/components/Alert'
import Badge from '@/shared/components/Badge'
import Card from '@/shared/components/Card'
import Loader from '@/shared/components/Loader'
import Table from '@/shared/components/Table'
import { useAuth } from '@/shared/auth/AuthContext'
import { formatMoney } from '@/shared/utils/formatMoney'
import {
  ROLE_DASHBOARD_DESCRIPTIONS,
  ROLE_VIEW_LABELS,
  countCriticalStock,
  countLowStock,
  formatDateTime,
  getMenuForRole,
  isBranch,
  isCentralWarehouse,
  stockLabel,
  sumStock
} from '@/shared/utils/roleViews'

function AccessGrid({ items }) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="text-lg font-bold text-slate-950">Pantallas disponibles para este rol</h2>
      <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {items.map((item) => (
          <Link key={item.path} to={item.path} className="rounded-2xl border border-slate-200 p-4 transition hover:border-slate-900 hover:bg-slate-50">
            <p className="font-bold text-slate-950">{item.label}</p>
            <p className="mt-1 text-sm leading-5 text-slate-500">{item.description || 'Acceso habilitado para tu rol.'}</p>
          </Link>
        ))}
      </div>
    </section>
  )
}

export default function DashboardPage() {
  const { usuario } = useAuth()
  const role = usuario?.rol
  const [inventario, setInventario] = useState([])
  const [movimientos, setMovimientos] = useState([])
  const [compras, setCompras] = useState([])
  const [reposiciones, setReposiciones] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let mounted = true

    async function loadDashboard() {
      try {
        const [inventarioData, movimientosData, comprasData, reposicionesData] = await Promise.all([
          listarInventario().catch(() => []),
          listarMovimientos({ limite: 100 }).catch(() => []),
          listarOrdenesCompra({ limite: 100 }).catch(() => []),
          listarReposiciones({ limite: 100 }).catch(() => [])
        ])
        if (!mounted) return
        setInventario(inventarioData)
        setMovimientos(movimientosData)
        setCompras(comprasData)
        setReposiciones(reposicionesData)
      } catch (err) {
        if (mounted) setError(err.message || 'No se pudo cargar el dashboard del almacén central')
      } finally {
        if (mounted) setLoading(false)
      }
    }

    loadDashboard()
    return () => { mounted = false }
  }, [])

  const central = useMemo(() => inventario.filter(isCentralWarehouse), [inventario])
  const sucursales = useMemo(() => inventario.filter(isBranch), [inventario])
  const roleMenu = useMemo(() => getMenuForRole(role), [role])

  const resumen = useMemo(() => {
    const solicitudesPendientes = reposiciones.filter((item) => ['ENVIADO', 'EN_REVISION'].includes(item.estado)).length
    const solicitudesAceptadas = reposiciones.filter((item) => item.estado === 'ACEPTADO').length
    const despachosEnTransito = reposiciones.filter((item) => item.estado === 'EN_TRANSITO').length
    const comprasAbiertas = compras.filter((item) => ['SOLICITADO', 'EN_TRANSITO'].includes(item.estado)).length
    const valorTotal = central.reduce((total, item) => total + Number(item.stockDisponible || 0) * Number(item.precioVenta || item.precio || 0), 0)

    return {
      solicitudesPendientes,
      solicitudesAceptadas,
      despachosEnTransito,
      comprasAbiertas,
      valorTotal
    }
  }, [central, compras, reposiciones])

  const movementColumns = [
    { key: 'fechaHora', header: 'Fecha', render: (row) => formatDateTime(row.fechaHora) },
    { key: 'producto', header: 'Producto' },
    { key: 'tipoMovimiento', header: 'Tipo', render: (row) => <Badge tone={row.tipoMovimiento === 'INGRESO' ? 'green' : 'red'}>{row.tipoMovimiento === 'INGRESO' ? 'Entrada' : 'Salida'}</Badge> },
    { key: 'motivoMovimiento', header: 'Motivo' },
    { key: 'cantidad', header: 'Cantidad' }
  ]

  if (loading) return <Loader message="Cargando dashboard del almacén central..." />

  return (
    <div className="space-y-6">
      <section className="rounded-3xl bg-slate-950 p-6 text-white shadow-sm">
        <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
          <div>
            <p className="text-sm font-semibold text-slate-400">{ROLE_VIEW_LABELS[role] || 'Supervisor de Almacén Central'}</p>
            <h1 className="mt-2 text-3xl font-black tracking-tight">Dashboard</h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-300">
              {ROLE_DASHBOARD_DESCRIPTIONS[role] || 'Vista operativa del almacén central.'}
            </p>
            <p className="mt-2 text-xs text-slate-400">
              Sesión activa: {usuario?.correoElectronico}. Ubicación: {usuario?.ubicacion || 'Almacén central'}.
            </p>
          </div>
          <Badge tone="green">{ROLE_VIEW_LABELS[role] || role}</Badge>
        </div>
      </section>

      {error && <Alert tone="error">{error}</Alert>}

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Card title="Productos almacén" value={central.length} description="Total de productos visibles" />
        <Card title="Stock crítico" value={countCriticalStock(central)} description="Productos agotados" />
        <Card title="Stock normal" value={central.filter((item) => stockLabel(item) === 'Disponible').length} description="Productos disponibles" />
        <Card title="Unidades totales" value={sumStock(central)} description="Stock acumulado" />
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Card title="Sucursales supervisadas" value={new Set(sucursales.map((item) => item.idUbicacion)).size} description="Con inventario registrado" />
        <Card title="Stock bajo en sucursales" value={countLowStock(sucursales) + countCriticalStock(sucursales)} description="Productos por reponer" />
        <Card title="Solicitudes pendientes" value={resumen.solicitudesPendientes} description="Enviadas o en revisión" />
        <Card title="Despachos por atender" value={resumen.solicitudesAceptadas} description={`En tránsito: ${resumen.despachosEnTransito}`} />
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        <Card title="Recepciones pendientes" value={resumen.comprasAbiertas} description="Órdenes de compra por verificar" />
        <Card title="Movimientos" value={movimientos.length} description="Ingresos, salidas y ajustes" />
        <Card title="Valor total estimado" value={formatMoney(resumen.valorTotal)} description="Stock central x precio venta" />
      </section>

      <AccessGrid items={roleMenu.map((item) => ({
        ...item,
        description: {
          '/dashboard': 'Resumen del almacén central.',
          '/inventario': 'Consultar productos, stock actual, stock mínimo y estado.',
          '/sucursales': 'Supervisar stock crítico, solicitudes y abastecimiento por sede.',
          '/recepciones': 'Recepcionar órdenes de compra creadas por el Administrador General.',
          '/solicitudes-reposicion': 'Evaluar solicitudes enviadas por sucursales.',
          '/despachos': 'Registrar envíos aceptados hacia sucursales.',
          '/movimientos': 'Consultar ingresos y salidas del almacén central.'
        }[item.path]
      }))} />

      <section className="space-y-3">
        <h2 className="text-lg font-bold text-slate-950">Movimientos recientes del almacén</h2>
        <Table columns={movementColumns} data={movimientos.filter(isCentralWarehouse).slice(0, 8)} keyField="idMovimiento" emptyMessage="No hay movimientos recientes." />
      </section>
    </div>
  )
}
