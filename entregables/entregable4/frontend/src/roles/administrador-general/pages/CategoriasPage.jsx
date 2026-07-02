import { useEffect, useMemo, useState } from 'react'
import { actualizarCategoria, crearCategoria, listarCategorias } from '@/shared/api/categoriaApi'
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
import Textarea from '@/shared/components/Textarea'
import { canManageCatalog, formatBooleanStatus, getApiErrorMessage } from '@/shared/utils/catalogo'

const emptyForm = {
  nombreCategoria: '',
  descripcion: '',
  isActivo: true
}

function preparePayload(form, isEdit) {
  const payload = {
    nombreCategoria: form.nombreCategoria.trim(),
    descripcion: form.descripcion.trim() || null
  }

  if (isEdit) payload.isActivo = form.isActivo

  return payload
}

export default function CategoriasPage() {
  const { usuario } = useAuth()
  const canManage = canManageCatalog(usuario?.rol)
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

  async function loadCategorias() {
    setLoading(true)
    setError('')

    try {
      const data = await listarCategorias({ incluirInactivas: canManage && showInactive })
      setCategorias(data)
    } catch (err) {
      setError(getApiErrorMessage(err, 'No se pudieron cargar las categorías'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadCategorias()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [showInactive, canManage])

  const filteredCategorias = useMemo(() => {
    const term = search.trim().toLowerCase()

    if (!term) return categorias

    return categorias.filter((categoria) => (
      categoria.nombreCategoria.toLowerCase().includes(term) ||
      (categoria.descripcion || '').toLowerCase().includes(term) ||
      String(categoria.idCategoria).includes(term)
    ))
  }, [categorias, search])

  function openCreateModal() {
    setEditing(null)
    setForm(emptyForm)
    setError('')
    setSuccess('')
    setIsModalOpen(true)
  }

  function openEditModal(categoria) {
    setEditing(categoria)
    setForm({
      nombreCategoria: categoria.nombreCategoria,
      descripcion: categoria.descripcion || '',
      isActivo: categoria.isActivo
    })
    setError('')
    setSuccess('')
    setIsModalOpen(true)
  }

  function handleChange(event) {
    const { name, value } = event.target
    setForm((prev) => ({ ...prev, [name]: value }))
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setSaving(true)
    setError('')
    setSuccess('')

    try {
      const payload = preparePayload(form, Boolean(editing))

      if (editing) {
        await actualizarCategoria(editing.idCategoria, payload)
        setSuccess('Categoría actualizada correctamente')
      } else {
        await crearCategoria(payload)
        setSuccess('Categoría creada correctamente')
      }

      setIsModalOpen(false)
      await loadCategorias()
    } catch (err) {
      setError(getApiErrorMessage(err, 'No se pudo guardar la categoría'))
    } finally {
      setSaving(false)
    }
  }

  async function toggleStatus(categoria) {
    setSaving(true)
    setError('')
    setSuccess('')

    try {
      await actualizarCategoria(categoria.idCategoria, { isActivo: !categoria.isActivo })
      setSuccess(`Categoría ${!categoria.isActivo ? 'activada' : 'desactivada'} correctamente`)
      await loadCategorias()
    } catch (err) {
      setError(getApiErrorMessage(err, 'No se pudo cambiar el estado de la categoría'))
    } finally {
      setSaving(false)
    }
  }

  const columns = [
    { key: 'idCategoria', header: 'ID', render: (row) => <span className="font-semibold text-slate-900">#{row.idCategoria}</span> },
    { key: 'nombreCategoria', header: 'Categoría', render: (row) => <span className="font-semibold text-slate-900">{row.nombreCategoria}</span> },
    { key: 'descripcion', header: 'Descripción', render: (row) => row.descripcion || <span className="text-slate-400">Sin descripción</span> },
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

  if (loading) return <Loader message="Cargando categorías..." />

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Catálogo"
        title="Categorías"
        description="Gestiona categorías generales del negocio. Actualmente tu base las mantiene como catálogo independiente."
        actions={canManage && <Button onClick={openCreateModal}>Nueva categoría</Button>}
      />

      {error && <Alert tone="error">{error}</Alert>}
      {success && <Alert tone="success">{success}</Alert>}

      <Card>
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <Input
            label="Buscar categoría"
            placeholder="Nombre, descripción o ID"
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
              Mostrar inactivas
            </label>
          )}
        </div>
      </Card>

      <Table
        columns={columns}
        data={filteredCategorias}
        keyField="idCategoria"
        emptyMessage="No hay categorías registradas."
      />

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={editing ? 'Editar categoría' : 'Nueva categoría'}
        description="Completa la información de la categoría."
        footer={(
          <>
            <Button type="button" variant="secondary" onClick={() => setIsModalOpen(false)}>Cancelar</Button>
            <Button type="submit" form="categoria-form" disabled={saving}>{saving ? 'Guardando...' : 'Guardar'}</Button>
          </>
        )}
      >
        <form id="categoria-form" className="space-y-4" onSubmit={handleSubmit}>
          <Input
            label="Nombre de categoría"
            name="nombreCategoria"
            value={form.nombreCategoria}
            onChange={handleChange}
            maxLength={100}
            required
          />
          <Textarea
            label="Descripción"
            name="descripcion"
            value={form.descripcion}
            onChange={handleChange}
            maxLength={200}
            placeholder="Descripción opcional"
          />
          {editing && (
            <Select label="Estado" name="isActivo" value={String(form.isActivo)} onChange={(event) => setForm((prev) => ({ ...prev, isActivo: event.target.value === 'true' }))}>
              <option value="true">Activa</option>
              <option value="false">Inactiva</option>
            </Select>
          )}
        </form>
      </Modal>
    </div>
  )
}
