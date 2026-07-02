import { useEffect, useMemo, useState } from 'react'
import { listarCategorias } from '@/shared/api/categoriaApi'
import { actualizarProducto, crearProducto, listarProductos } from '@/shared/api/productoApi'
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
import { canManageCatalog, formatBooleanStatus, getApiErrorMessage, normalizeDecimal } from '@/shared/utils/catalogo'
import { formatMoney } from '@/shared/utils/formatMoney'

const emptyForm = {
  codigoBarras: '',
  nombreProducto: '',
  idCategoria: '',
  precioVenta: '',
  porcentajeIgv: '18.00',
  isActivo: true
}

function sanitizeDecimalInput(value, { min = 0, max = null } = {}) {
  if (value === '') return ''

  const text = String(value).replace(/-/g, '')
  const number = Number(text)
  if (!Number.isFinite(number)) return ''
  if (number < min) return String(min)
  if (max !== null && number > max) return String(max)

  return text
}

function preparePayload(form, isEdit) {
  const payload = {
    codigoBarras: form.codigoBarras.trim(),
    nombreProducto: form.nombreProducto.trim(),
    idCategoria: form.idCategoria ? Number(form.idCategoria) : null,
    precioVenta: Number(form.precioVenta),
    porcentajeIgv: Number(form.porcentajeIgv)
  }

  if (isEdit) payload.isActivo = form.isActivo

  return payload
}

export default function ProductosPage() {
  const { usuario } = useAuth()
  const canManage = canManageCatalog(usuario?.rol)
  const [productos, setProductos] = useState([])
  const [categorias, setCategorias] = useState([])
  const [search, setSearch] = useState('')
  const [showInactive, setShowInactive] = useState(canManage)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState(emptyForm)

  async function loadProductos() {
    setLoading(true)
    setError('')

    try {
      const data = await listarProductos({ incluirInactivos: canManage && showInactive })
      setProductos(data)
    } catch (err) {
      setError(getApiErrorMessage(err, 'No se pudieron cargar los productos'))
    } finally {
      setLoading(false)
    }
  }

  async function loadCategorias() {
    try {
      const data = await listarCategorias({ incluirInactivas: false })
      setCategorias(data)
    } catch {
      setCategorias([])
    }
  }

  useEffect(() => {
    loadProductos()
    loadCategorias()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [showInactive, canManage])

  const filteredProductos = useMemo(() => {
    const term = search.trim().toLowerCase()

    if (!term) return productos

    return productos.filter((producto) => (
      producto.nombreProducto.toLowerCase().includes(term) ||
      producto.codigoBarras.toLowerCase().includes(term) ||
      producto.categoria?.toLowerCase().includes(term) ||
      String(producto.idProducto).includes(term)
    ))
  }, [productos, search])

  function openCreateModal() {
    setEditing(null)
    setForm(emptyForm)
    setSuccess('')
    setError('')
    setIsModalOpen(true)
  }

  function openEditModal(producto) {
    setEditing(producto)
    setForm({
      codigoBarras: producto.codigoBarras,
      nombreProducto: producto.nombreProducto,
      idCategoria: producto.idCategoria ? String(producto.idCategoria) : '',
      precioVenta: normalizeDecimal(producto.precioVenta),
      porcentajeIgv: normalizeDecimal(producto.porcentajeIgv),
      isActivo: producto.isActivo
    })
    setSuccess('')
    setError('')
    setIsModalOpen(true)
  }

  function handleChange(event) {
    const { name, value, type, checked } = event.target
    let nextValue = value

    if (name === 'precioVenta') nextValue = sanitizeDecimalInput(value, { min: 0 })
    if (name === 'porcentajeIgv') nextValue = sanitizeDecimalInput(value, { min: 0, max: 100 })

    setForm((prev) => ({ ...prev, [name]: type === 'checkbox' ? checked : nextValue }))
  }

  function validateForm() {
    if (Number(form.precioVenta) <= 0) return 'El precio de venta debe ser mayor que cero.'
    if (Number(form.porcentajeIgv) < 0 || Number(form.porcentajeIgv) > 100) return 'El IGV debe estar entre 0% y 100%.'
    return ''
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setSuccess('')

    const validationError = validateForm()
    if (validationError) {
      setError(validationError)
      return
    }

    setSaving(true)

    try {
      const payload = preparePayload(form, Boolean(editing))

      if (editing) {
        await actualizarProducto(editing.idProducto, payload)
        setSuccess('Producto actualizado correctamente')
      } else {
        await crearProducto(payload)
        setSuccess('Producto creado correctamente')
      }

      setIsModalOpen(false)
      await loadProductos()
    } catch (err) {
      setError(getApiErrorMessage(err, 'No se pudo guardar el producto'))
    } finally {
      setSaving(false)
    }
  }

  async function toggleStatus(producto) {
    setSaving(true)
    setError('')
    setSuccess('')

    try {
      await actualizarProducto(producto.idProducto, { isActivo: !producto.isActivo })
      setSuccess(`Producto ${!producto.isActivo ? 'activado' : 'desactivado'} correctamente`)
      await loadProductos()
    } catch (err) {
      setError(getApiErrorMessage(err, 'No se pudo cambiar el estado del producto'))
    } finally {
      setSaving(false)
    }
  }

  const columns = [
    { key: 'idProducto', header: 'ID', render: (row) => <span className="font-semibold text-slate-900">#{row.idProducto}</span> },
    { key: 'codigoBarras', header: 'Código' },
    { key: 'nombreProducto', header: 'Producto', render: (row) => <span className="font-semibold text-slate-900">{row.nombreProducto}</span> },
    { key: 'categoria', header: 'Categoría', render: (row) => row.categoria || <span className="text-slate-400">Sin categoría</span> },
    { key: 'precioVenta', header: 'Precio', render: (row) => formatMoney(row.precioVenta) },
    { key: 'porcentajeIgv', header: 'IGV', render: (row) => `${Number(row.porcentajeIgv).toFixed(2)}%` },
    {
      key: 'isActivo',
      header: 'Estado',
      render: (row) => <Badge tone={row.isActivo ? 'green' : 'red'}>{formatBooleanStatus(row.isActivo)}</Badge>
    },
    {
      key: 'acciones',
      header: 'Acciones',
      render: (row) => canManage ? (
        <div className="flex flex-wrap gap-2">
          <Button type="button" variant="secondary" className="px-3 py-2" onClick={() => openEditModal(row)}>
            Editar
          </Button>
          <Button
            type="button"
            variant={row.isActivo ? 'danger' : 'secondary'}
            className="px-3 py-2"
            disabled={saving}
            onClick={() => toggleStatus(row)}
          >
            {row.isActivo ? 'Desactivar' : 'Activar'}
          </Button>
        </div>
      ) : <span className="text-slate-400">Solo lectura</span>
    }
  ]

  if (loading) return <Loader message="Cargando productos..." />

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Catálogo"
        title="Productos"
        description="Administra los productos que luego se usarán en inventario, ventas, órdenes de compra y reposiciones. Cada producto puede asociarse a una categoría para facilitar búsquedas y filtros."
        actions={canManage && <Button onClick={openCreateModal}>Nuevo producto</Button>}
      />

      {error && <Alert tone="error">{error}</Alert>}
      {success && <Alert tone="success">{success}</Alert>}

      <Card>
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <Input
            label="Buscar producto"
            placeholder="Código, nombre, categoría o ID"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            className="md:w-80"
          />
          {canManage && (
            <label className="flex items-center gap-2 text-sm font-medium text-slate-700">
              <input
                type="checkbox"
                checked={showInactive}
                onChange={(event) => setShowInactive(event.target.checked)}
                className="h-4 w-4 rounded border-slate-300"
              />
              Mostrar inactivos
            </label>
          )}
        </div>
      </Card>

      <Table
        columns={columns}
        data={filteredProductos}
        keyField="idProducto"
        emptyMessage="No hay productos registrados."
      />

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={editing ? 'Editar producto' : 'Nuevo producto'}
        description="Completa los datos básicos del producto."
        footer={(
          <>
            <Button type="button" variant="secondary" onClick={() => setIsModalOpen(false)}>Cancelar</Button>
            <Button type="submit" form="producto-form" disabled={saving}>{saving ? 'Guardando...' : 'Guardar'}</Button>
          </>
        )}
      >
        <form id="producto-form" className="grid gap-4 md:grid-cols-2" onSubmit={handleSubmit}>
          <Input
            label="Código de barras"
            name="codigoBarras"
            value={form.codigoBarras}
            onChange={handleChange}
            maxLength={50}
            required
          />
          <Input
            label="Nombre del producto"
            name="nombreProducto"
            value={form.nombreProducto}
            onChange={handleChange}
            maxLength={150}
            required
          />
          <Select label="Categoría" name="idCategoria" value={form.idCategoria} onChange={handleChange}>
            <option value="">Sin categoría</option>
            {categorias.map((categoria) => (
              <option key={categoria.idCategoria} value={categoria.idCategoria}>{categoria.nombreCategoria}</option>
            ))}
          </Select>
          <Input
            label="Precio de venta"
            name="precioVenta"
            type="number"
            min="0.01"
            step="0.01"
            value={form.precioVenta}
            onChange={handleChange}
            required
          />
          <Input
            label="IGV (%)"
            name="porcentajeIgv"
            type="number"
            min="0"
            max="100"
            step="0.01"
            value={form.porcentajeIgv}
            onChange={handleChange}
            required
          />
          {editing && (
            <Select label="Estado" name="isActivo" value={String(form.isActivo)} onChange={(event) => setForm((prev) => ({ ...prev, isActivo: event.target.value === 'true' }))}>
              <option value="true">Activo</option>
              <option value="false">Inactivo</option>
            </Select>
          )}
        </form>
      </Modal>
    </div>
  )
}
