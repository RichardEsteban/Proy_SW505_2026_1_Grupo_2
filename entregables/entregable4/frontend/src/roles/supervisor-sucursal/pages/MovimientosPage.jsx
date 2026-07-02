import { useEffect, useMemo, useState } from 'react'
import { listarMovimientos } from '@/shared/api/inventarioApi'
import { listarUbicaciones } from '@/shared/api/ubicacionApi'
import { useAuth } from '@/shared/auth/AuthContext'
import Alert from '@/shared/components/Alert'
import Badge from '@/shared/components/Badge'
import Card from '@/shared/components/Card'
import Input from '@/shared/components/Input'
import Loader from '@/shared/components/Loader'
import PageHeader from '@/shared/components/PageHeader'
import Select from '@/shared/components/Select'
import Table from '@/shared/components/Table'
import { canSeeAllLocations } from '@/shared/utils/roles'
import { formatDateTime } from '@/shared/utils/roleViews'

export default function MovimientosPage() {
  const { usuario } = useAuth()
  const globalView = canSeeAllLocations(usuario?.rol)
  const [movimientos, setMovimientos] = useState([])
  const [ubicaciones, setUbicaciones] = useState([])
  const [tipo, setTipo] = useState('')
  const [ubicacion, setUbicacion] = useState(globalView ? '' : usuario?.idUbicacion || '')
  const [desde, setDesde] = useState('')
  const [hasta, setHasta] = useState('')
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  async function loadData() {
    setError('')
    try {
      const [movimientosData, ubicacionesData] = await Promise.all([
        listarMovimientos({ idUbicacion: ubicacion || undefined, desde: desde || undefined, hasta: hasta || undefined, limite: 250 }),
        globalView ? listarUbicaciones({ incluirInactivas: false }) : Promise.resolve([])
      ])
      setMovimientos(movimientosData)
      setUbicaciones(ubicacionesData)
    } catch (err) {
      setError(err.message || 'No se pudieron cargar los movimientos')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ubicacion, desde, hasta])

  const filtered = useMemo(() => {
    const term = search.trim().toLowerCase()
    return movimientos.filter((item) => {
      const matchTipo = !tipo || item.tipoMovimiento === tipo
      const matchTerm = !term || [item.producto, item.ubicacion, item.motivoMovimiento, item.usuario, item.idMovimiento]
        .some((value) => String(value || '').toLowerCase().includes(term))
      return matchTipo && matchTerm
    })
  }, [movimientos, tipo, search])

  const resumen = useMemo(() => ({
    total: filtered.length,
    entradas: filtered.filter((item) => item.tipoMovimiento === 'INGRESO').length,
    salidas: filtered.filter((item) => item.tipoMovimiento === 'SALIDA').length,
    ajustes: filtered.filter((item) => ['AJUSTE', 'MERMA'].includes(item.motivoMovimiento)).length
  }), [filtered])

  const columns = [
    { key: 'idMovimiento', header: 'N°', render: (row) => <span className="font-semibold text-slate-950">MOV-{String(row.idMovimiento).padStart(5, '0')}</span> },
    { key: 'fechaHora', header: 'Fecha', render: (row) => formatDateTime(row.fechaHora) },
    { key: 'producto', header: 'Producto', render: (row) => <span className="font-semibold text-slate-950">{row.producto}</span> },
    { key: 'ubicacion', header: 'Ubicación' },
    { key: 'tipoMovimiento', header: 'Tipo', render: (row) => <Badge tone={row.tipoMovimiento === 'INGRESO' ? 'green' : 'red'}>{row.tipoMovimiento === 'INGRESO' ? 'Entrada' : 'Salida'}</Badge> },
    { key: 'motivoMovimiento', header: 'Motivo' },
    { key: 'cantidad', header: 'Cantidad', render: (row) => <span className="font-bold text-slate-950">{row.cantidad}</span> },
    { key: 'usuario', header: 'Usuario' }
  ]

  if (loading) return <Loader message="Cargando movimientos..." />

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Movimientos"
        title="Historial de cambios de stock"
        description="Entrada indica aumento de stock y salida indica disminución. Los ajustes/mermas se muestran como movimientos especiales de revisión operativa."
      />

      {error && <Alert tone="error">{error}</Alert>}

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Card title="Total movimientos" value={resumen.total} description="Con filtros actuales" />
        <Card title="Entradas" value={resumen.entradas} description="Aumentos de stock" />
        <Card title="Salidas" value={resumen.salidas} description="Disminuciones de stock" />
        <Card title="Ajustes / merma" value={resumen.ajustes} description="Movimientos manuales" />
      </section>

      <Card>
        <div className="grid gap-3 lg:grid-cols-5">
          <Input label="Buscar" placeholder="Producto, ubicación, usuario o motivo" value={search} onChange={(event) => setSearch(event.target.value)} />
          <Select label="Tipo" value={tipo} onChange={(event) => setTipo(event.target.value)}>
            <option value="">Todos</option>
            <option value="INGRESO">Entrada</option>
            <option value="SALIDA">Salida</option>
          </Select>
          <Select label="Sucursal / ubicación" value={ubicacion} onChange={(event) => setUbicacion(event.target.value)} disabled={!globalView}>
            <option value="">{globalView ? 'Todas' : usuario?.ubicacion}</option>
            {ubicaciones.map((item) => <option key={item.idUbicacion} value={item.idUbicacion}>{item.nombreUbicacion}</option>)}
          </Select>
          <Input label="Desde" type="date" value={desde} onChange={(event) => setDesde(event.target.value)} />
          <Input label="Hasta" type="date" value={hasta} onChange={(event) => setHasta(event.target.value)} />
        </div>
      </Card>

      <Table columns={columns} data={filtered} keyField="idMovimiento" emptyMessage="No hay movimientos con los filtros actuales." />
    </div>
  )
}
