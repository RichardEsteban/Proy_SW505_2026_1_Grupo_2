import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { listarInventario, listarMovimientos } from '@/shared/api/inventarioApi'
import { listarReposiciones } from '@/shared/api/reposicionApi'
import { listarAlertas } from '@/shared/api/alertaApi'
import { useAuth } from '@/shared/auth/AuthContext'
import Badge from '@/shared/components/Badge'
import Button from '@/shared/components/Button'
import Card from '@/shared/components/Card'
import Loader from '@/shared/components/Loader'
import Table from '@/shared/components/Table'
import { ROLE_DASHBOARD_DESCRIPTIONS, ROLE_VIEW_LABELS, countCriticalStock, countLowStock, formatDateTime, stockLabel, stockTone, sumStock } from '@/shared/utils/roleViews'

function groupByDay(items = []) {
  const days = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb']
  const result = days.map((dia) => ({ dia, cantidad: 0 }))

  items.forEach((item) => {
    if (!item.fechaHora) return
    const date = new Date(item.fechaHora)
    result[date.getDay()].cantidad += Number(item.cantidad || 1)
  })

  return [...result.slice(1), result[0]]
}

function AccessGrid({ items }) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="text-lg font-bold text-slate-950">Accesos rápidos</h2>
      <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-5">
        {items.map((item) => (
          <Link key={item.path} to={item.path} className="rounded-2xl border border-slate-200 p-4 transition hover:border-slate-900 hover:bg-slate-50">
            <p className="font-bold text-slate-950">{item.label}</p>
            <p className="mt-1 text-sm leading-5 text-slate-500">{item.description}</p>
          </Link>
        ))}
      </div>
    </section>
  )
}

export default function DashboardPage() {
  const { usuario } = useAuth()
  const [inventario, setInventario] = useState([])
  const [movimientos, setMovimientos] = useState([])
  const [reposiciones, setReposiciones] = useState([])
  const [alertas, setAlertas] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let mounted = true

    async function loadDashboard() {
      setError('')
      setLoading(true)
      try {
        const idUbicacion = usuario?.idUbicacion
        const [inventarioData, movimientosData, reposicionesData, alertasData] = await Promise.all([
          listarInventario({ idUbicacion }),
          listarMovimientos({ idUbicacion, limite: 80 }),
          listarReposiciones({ idUbicacionDestino: idUbicacion, limite: 80 }),
          listarAlertas({ idUbicacion, estado: 'PENDIENTE' }).catch(() => [])
        ])
        if (!mounted) return
        setInventario(inventarioData)
        setMovimientos(movimientosData)
        setReposiciones(reposicionesData)
        setAlertas(alertasData)
      } catch (err) {
        if (mounted) setError(err.message || 'No se pudo cargar el dashboard de sucursal')
      } finally {
        if (mounted) setLoading(false)
      }
    }

    loadDashboard()
    return () => { mounted = false }
  }, [usuario?.idUbicacion])

  const resumen = useMemo(() => ({
    productos: inventario.length,
    unidades: sumStock(inventario),
    stockBajo: countLowStock(inventario),
    stockCritico: countCriticalStock(inventario),
    solicitudesAbiertas: reposiciones.filter((item) => !['RECIBIDA', 'RECHAZADA', 'CANCELADA'].includes(item.estado)).length,
    recepcionesPendientes: reposiciones.filter((item) => item.estado === 'EN_TRANSITO').length,
    alertasPendientes: alertas.length
  }), [inventario, reposiciones, alertas])

  const week = groupByDay(movimientos)
  const max = Math.max(...week.map((item) => item.cantidad), 1)

  const inventarioColumns = [
    { key: 'codigoBarras', header: 'Código' },
    { key: 'producto', header: 'Producto' },
    { key: 'stockDisponible', header: 'Stock' },
    { key: 'estado', header: 'Estado', render: (row) => <Badge tone={stockTone(row)}>{stockLabel(row)}</Badge> }
  ]

  const reposicionColumns = [
    { key: 'idSolicitud', header: 'Solicitud', render: (row) => <span className="font-semibold text-slate-950">SOL-{String(row.idSolicitud).padStart(4, '0')}</span> },
    { key: 'fechaSolicitud', header: 'Fecha', render: (row) => formatDateTime(row.fechaSolicitud) },
    { key: 'estado', header: 'Estado', render: (row) => <Badge tone={row.estado === 'EN_TRANSITO' ? 'amber' : 'slate'}>{row.estado}</Badge> },
    { key: 'origen', header: 'Origen', render: (row) => row.ubicacionOrigen || '-' }
  ]

  if (loading) return <Loader message="Cargando dashboard de sucursal..." />

  return (
    <div className="space-y-6">
      <section className="rounded-3xl bg-slate-950 p-6 text-white shadow-sm">
        <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
          <div>
            <p className="text-sm font-semibold text-slate-400">{ROLE_VIEW_LABELS[usuario?.rol] || 'Supervisor de Sucursal'}</p>
            <h1 className="mt-2 text-3xl font-black tracking-tight">Dashboard</h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-300">
              {ROLE_DASHBOARD_DESCRIPTIONS[usuario?.rol] || 'Vista operativa de la sucursal asignada.'}
            </p>
            <p className="mt-2 text-xs text-slate-400">Sucursal asignada: {usuario?.ubicacion || 'Sin ubicación'}.</p>
          </div>
          <Badge tone="green">{usuario?.ubicacion || 'Sucursal'}</Badge>
        </div>
      </section>

      {error && <div className="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">{error}</div>}

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Card title="Productos" value={resumen.productos} description="En mi inventario" />
        <Card title="Unidades" value={resumen.unidades} description="Stock acumulado" />
        <Card title="Stock bajo/crítico" value={resumen.stockBajo + resumen.stockCritico} description={`${resumen.stockCritico} sin stock`} />
        <Card title="Alertas pendientes" value={resumen.alertasPendientes} description="Por revisar" />
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        <Card title="Solicitudes abiertas" value={resumen.solicitudesAbiertas} description="Enviadas, revisión, aceptadas o tránsito" />
        <Card title="Recepciones pendientes" value={resumen.recepcionesPendientes} description="Pedidos en tránsito" />
        <Card title="Movimientos" value={movimientos.length} description="Últimos registros" />
      </section>

      <AccessGrid items={[
        { label: 'Inventario', path: '/inventario', description: 'Ver productos, stock actual y stock mínimo.' },
        { label: 'Nueva solicitud', path: '/solicitudes-reposicion', description: 'Pedir productos al almacén central.' },
        { label: 'Recepciones', path: '/recepciones', description: 'Confirmar productos enviados por almacén.' },
        { label: 'Alertas de stock', path: '/alertas-stock', description: 'Revisar productos en mínimo o sin stock.' },
        { label: 'Movimientos', path: '/movimientos', description: 'Consultar entradas y salidas de mi sucursal.' }
      ]} />

      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="text-lg font-bold text-slate-950">Movimientos por semana</h2>
        <p className="mt-1 text-sm text-slate-500">Cantidad movida por día en la sucursal asignada.</p>
        <div className="mt-5 grid grid-cols-7 gap-2">
          {week.map((item) => (
            <div key={item.dia} className="flex flex-col items-center gap-2">
              <div className="flex h-32 w-full items-end rounded-xl bg-slate-100 px-2">
                <div className="w-full rounded-t-xl bg-slate-900" style={{ height: `${Math.max(8, (item.cantidad / max) * 100)}%` }} />
              </div>
              <p className="text-xs font-bold text-slate-700">{item.dia}</p>
              <p className="text-xs text-slate-500">{item.cantidad}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-2">
        <div className="space-y-3">
          <div className="flex items-center justify-between gap-3">
            <h2 className="text-lg font-bold text-slate-950">Productos críticos</h2>
            <Button as={Link} to="/inventario" variant="secondary">Ver inventario</Button>
          </div>
          <Table columns={inventarioColumns} data={inventario.filter((item) => stockLabel(item) !== 'Disponible').slice(0, 6)} keyField="idInventario" emptyMessage="No hay productos críticos en tu sucursal." />
        </div>
        <div className="space-y-3">
          <div className="flex items-center justify-between gap-3">
            <h2 className="text-lg font-bold text-slate-950">Reposiciones recientes</h2>
            <Button as={Link} to="/solicitudes-reposicion" variant="secondary">Ver solicitudes</Button>
          </div>
          <Table columns={reposicionColumns} data={reposiciones.slice(0, 6)} keyField="idSolicitud" emptyMessage="No hay solicitudes recientes." />
        </div>
      </section>
    </div>
  )
}
