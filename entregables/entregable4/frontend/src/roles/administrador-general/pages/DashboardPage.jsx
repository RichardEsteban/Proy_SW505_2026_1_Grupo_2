import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { getResumen } from '@/shared/api/dashboardApi'
import { listarInventario, listarMovimientos } from '@/shared/api/inventarioApi'
import Alert from '@/shared/components/Alert'
import Badge from '@/shared/components/Badge'
import Button from '@/shared/components/Button'
import Card from '@/shared/components/Card'
import Loader from '@/shared/components/Loader'
import Table from '@/shared/components/Table'
import { useAuth } from '@/shared/auth/AuthContext'
import { formatMoney } from '@/shared/utils/formatMoney'
import {
  ROLE_VIEW_LABELS,
  countLowStock,
  formatDateTime,
  stockLabel,
  stockTone,
  sumStock
} from '@/shared/utils/roleViews'

const emptyResumen = {
  totalVentas: 0,
  cantidadVentas: 0,
  productosVendidos: 0,
  ticketPromedio: 0,
  productosConStockBajo: 0,
  alertasPendientes: 0
}

function AccessGrid({ items }) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="text-lg font-bold text-slate-950">Módulos del Administrador General</h2>
      <p className="mt-1 text-sm text-slate-500">
        Estos accesos corresponden a los casos de uso definidos para este rol.
      </p>
      <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
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
  const [resumen, setResumen] = useState(emptyResumen)
  const [inventario, setInventario] = useState([])
  const [movimientos, setMovimientos] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let mounted = true

    async function loadDashboard() {
      setLoading(true)
      setError('')

      try {
        const [resumenData, inventarioData, movimientosData] = await Promise.all([
          getResumen().catch(() => emptyResumen),
          listarInventario().catch(() => []),
          listarMovimientos({ limite: 10 }).catch(() => [])
        ])

        if (!mounted) return
        setResumen(resumenData)
        setInventario(inventarioData)
        setMovimientos(movimientosData)
      } catch (err) {
        if (mounted) setError(err.message || 'No se pudo cargar el dashboard administrativo')
      } finally {
        if (mounted) setLoading(false)
      }
    }

    loadDashboard()

    return () => {
      mounted = false
    }
  }, [])

  const stockBajo = useMemo(() => countLowStock(inventario), [inventario])

  const actions = [
    { label: 'Usuarios y roles', path: '/usuarios', description: 'Registrar empleados, asignar roles, editar y activar/desactivar accesos.' },
    { label: 'Productos', path: '/productos', description: 'Registrar, editar, filtrar y activar/desactivar productos.' },
    { label: 'Categorías', path: '/categorias', description: 'Gestionar categorías del catálogo de productos.' },
    { label: 'Proveedores', path: '/proveedores', description: 'Administrar proveedores y sus datos de contacto.' },
    { label: 'Orden de compra', path: '/ordenes-compra', description: 'Crear órdenes de compra para proveedores sin actualizar stock hasta su recepción.' },
    { label: 'Ubicaciones', path: '/ubicaciones', description: 'Gestionar almacén central y sucursales desde una sola vista.' },
    { label: 'Reportes', path: '/reportes', description: 'Consultar reportes globales de ventas, inventario y movimientos.' }
  ]

  const movementColumns = [
    { key: 'fechaHora', header: 'Fecha', render: (row) => formatDateTime(row.fechaHora) },
    { key: 'producto', header: 'Producto' },
    { key: 'ubicacion', header: 'Ubicación' },
    { key: 'tipoMovimiento', header: 'Tipo', render: (row) => <Badge tone={row.tipoMovimiento === 'INGRESO' ? 'green' : 'red'}>{row.tipoMovimiento === 'INGRESO' ? 'Entrada' : 'Salida'}</Badge> },
    { key: 'cantidad', header: 'Cantidad', render: (row) => <span className="font-bold text-slate-950">{row.cantidad}</span> }
  ]

  if (loading) return <Loader message="Cargando dashboard administrativo..." />

  return (
    <div className="space-y-6">
      <section className="rounded-3xl bg-slate-950 p-6 text-white shadow-sm">
        <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
          <div>
            <p className="text-sm font-semibold text-slate-400">{ROLE_VIEW_LABELS.ADMIN}</p>
            <h1 className="mt-2 text-3xl font-black tracking-tight">Dashboard administrativo</h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-300">
              Vista general del negocio: ventas, productos vendidos, inventario, alertas de stock, ubicaciones operativas y movimientos recientes.
            </p>
            <p className="mt-2 text-xs text-slate-400">
              Sesión activa: {usuario?.correoElectronico}. Ubicación: {usuario?.ubicacion || 'Sin ubicación'}.
            </p>
          </div>
          <Badge tone="green">Administrador General</Badge>
        </div>
      </section>

      {error && <Alert tone="warning">{error}. La vista cargó, pero algunos indicadores no respondieron.</Alert>}

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Card title="Ventas totales" value={formatMoney(resumen.totalVentas)} description={`${resumen.cantidadVentas || 0} venta(s) registradas`} />
        <Card title="Productos vendidos" value={resumen.productosVendidos || 0} description="Unidades registradas en ventas" />
        <Card title="Inventario total" value={sumStock(inventario)} description={`${inventario.length} producto(s) en ubicaciones`} />
        <Card title="Alertas de stock" value={resumen.alertasPendientes || resumen.productosConStockBajo || stockBajo} description="Stock bajo o crítico" />
      </section>

      <AccessGrid items={actions} />

      <section className="grid gap-4 xl:grid-cols-[1fr_22rem]">
        <div className="space-y-3">
          <h2 className="text-lg font-bold text-slate-950">Movimientos recientes</h2>
          <Table columns={movementColumns} data={movimientos} keyField="idMovimiento" emptyMessage="No hay movimientos recientes." />
        </div>

        <Card>
          <h2 className="text-lg font-bold text-slate-950">Estado rápido de inventario</h2>
          <p className="mt-1 text-sm text-slate-500">Resumen de los primeros productos cargados en ubicaciones.</p>
          <div className="mt-4 space-y-3">
            {inventario.slice(0, 5).map((item) => (
              <div key={item.idInventario} className="flex items-center justify-between gap-3 rounded-2xl border border-slate-100 p-3">
                <div className="min-w-0">
                  <p className="truncate text-sm font-bold text-slate-950">{item.producto}</p>
                  <p className="text-xs text-slate-500">{item.ubicacion}</p>
                </div>
                <Badge tone={stockTone(item)}>{stockLabel(item)}</Badge>
              </div>
            ))}
            {inventario.length === 0 && <p className="text-sm text-slate-500">No hay inventario registrado.</p>}
          </div>
          <Button as={Link} to="/productos" variant="secondary" className="mt-4 w-full">Ver productos</Button>
        </Card>
      </section>
    </div>
  )
}
