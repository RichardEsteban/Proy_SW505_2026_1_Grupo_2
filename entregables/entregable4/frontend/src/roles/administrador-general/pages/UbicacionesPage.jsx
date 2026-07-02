import { useEffect, useMemo, useState } from 'react'
import { actualizarUbicacion, crearUbicacion, listarUbicaciones } from '@/shared/api/ubicacionApi'
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
import { booleanStatus, booleanTone, getApiErrorMessage, locationTypeLabel } from '@/shared/utils/admin'

const initialForm = {
  nombreUbicacion: '',
  tipoUbicacion: 'SUCURSAL',
  direccion: '',
  isActivo: true
}

function normalizeForm(ubicacion = null) {
  if (!ubicacion) return initialForm

  return {
    nombreUbicacion: ubicacion.nombreUbicacion || '',
    tipoUbicacion: ubicacion.tipoUbicacion || 'SUCURSAL',
    direccion: ubicacion.direccion || '',
    isActivo: Boolean(ubicacion.isActivo)
  }
}

function validateForm(form) {
  const errors = {}

  if (!form.nombreUbicacion.trim()) errors.nombreUbicacion = 'Ingresa el nombre de la ubicación.'
  if (form.nombreUbicacion.trim().length > 0 && form.nombreUbicacion.trim().length < 2) errors.nombreUbicacion = 'El nombre debe tener al menos 2 caracteres.'
  if (!form.tipoUbicacion) errors.tipoUbicacion = 'Selecciona el tipo de ubicación.'
  if (!form.direccion.trim()) errors.direccion = 'Ingresa la dirección.'
  if (form.direccion.trim().length > 0 && form.direccion.trim().length < 2) errors.direccion = 'La dirección debe tener al menos 2 caracteres.'

  return errors
}

export default function UbicacionesPage() {
  const [ubicaciones, setUbicaciones] = useState([])
  const [search, setSearch] = useState('')
  const [tipoFilter, setTipoFilter] = useState('TODOS')
  const [estadoFilter, setEstadoFilter] = useState('TODOS')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [modalOpen, setModalOpen] = useState(false)
  const [editingUbicacion, setEditingUbicacion] = useState(null)
  const [form, setForm] = useState(initialForm)
  const [formErrors, setFormErrors] = useState({})

  async function loadUbicaciones() {
    setError('')

    try {
      const data = await listarUbicaciones({ incluirInactivas: true })
      setUbicaciones(data)
    } catch (err) {
      setError(getApiErrorMessage(err, 'No se pudieron cargar las ubicaciones'))
    }
  }

  useEffect(() => {
    let mounted = true

    async function initialLoad() {
      setLoading(true)
      await loadUbicaciones()
      if (mounted) setLoading(false)
    }

    initialLoad()

    return () => {
      mounted = false
    }
  }, [])

  const filteredUbicaciones = useMemo(() => {
    const term = search.trim().toLowerCase()

    return ubicaciones.filter((ubicacion) => {
      const matchesSearch = !term || [
        ubicacion.nombreUbicacion,
        ubicacion.tipoUbicacion,
        ubicacion.direccion,
        String(ubicacion.idUbicacion)
      ].some((value) => String(value || '').toLowerCase().includes(term))

      const matchesTipo = tipoFilter === 'TODOS' || ubicacion.tipoUbicacion === tipoFilter
      const matchesEstado = estadoFilter === 'TODOS' || String(Boolean(ubicacion.isActivo)) === estadoFilter

      return matchesSearch && matchesTipo && matchesEstado
    })
  }, [ubicaciones, search, tipoFilter, estadoFilter])

  const resumen = useMemo(() => ({
    total: ubicaciones.length,
    almacenes: ubicaciones.filter((ubicacion) => ubicacion.tipoUbicacion === 'ALMACEN').length,
    sucursales: ubicaciones.filter((ubicacion) => ubicacion.tipoUbicacion === 'SUCURSAL').length,
    activas: ubicaciones.filter((ubicacion) => ubicacion.isActivo).length,
    inactivas: ubicaciones.filter((ubicacion) => !ubicacion.isActivo).length
  }), [ubicaciones])

  function openCreateModal() {
    setEditingUbicacion(null)
    setForm(initialForm)
    setFormErrors({})
    setError('')
    setSuccess('')
    setModalOpen(true)
  }

  function openEditModal(ubicacion) {
    setEditingUbicacion(ubicacion)
    setForm(normalizeForm(ubicacion))
    setFormErrors({})
    setError('')
    setSuccess('')
    setModalOpen(true)
  }

  function closeModal() {
    if (saving) return
    setModalOpen(false)
    setEditingUbicacion(null)
    setForm(initialForm)
    setFormErrors({})
  }

  function updateForm(field, value) {
    setForm((current) => ({ ...current, [field]: value }))
    setFormErrors((current) => ({ ...current, [field]: undefined }))
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setSuccess('')

    const errors = validateForm(form)
    setFormErrors(errors)
    if (Object.keys(errors).length > 0) return

    const payload = {
      nombreUbicacion: form.nombreUbicacion.trim(),
      tipoUbicacion: form.tipoUbicacion,
      direccion: form.direccion.trim(),
      ...(editingUbicacion ? { isActivo: form.isActivo } : {})
    }

    setSaving(true)

    try {
      if (editingUbicacion) {
        await actualizarUbicacion(editingUbicacion.idUbicacion, payload)
        setSuccess('Ubicación actualizada correctamente.')
      } else {
        await crearUbicacion(payload)
        setSuccess('Ubicación registrada correctamente.')
      }

      await loadUbicaciones()
      setModalOpen(false)
      setEditingUbicacion(null)
      setForm(initialForm)
      setFormErrors({})
    } catch (err) {
      setError(getApiErrorMessage(err, 'No se pudo guardar la ubicación'))
    } finally {
      setSaving(false)
    }
  }

  async function toggleEstado(ubicacion) {
    setError('')
    setSuccess('')

    try {
      await actualizarUbicacion(ubicacion.idUbicacion, { isActivo: !ubicacion.isActivo })
      setSuccess(ubicacion.isActivo ? 'Ubicación desactivada correctamente.' : 'Ubicación activada correctamente.')
      await loadUbicaciones()
    } catch (err) {
      setError(getApiErrorMessage(err, 'No se pudo cambiar el estado de la ubicación'))
    }
  }

  const columns = [
    {
      key: 'nombreUbicacion',
      header: 'Ubicación',
      render: (row) => (
        <div>
          <p className="font-bold text-slate-950">{row.nombreUbicacion}</p>
          <p className="text-xs text-slate-500">ID #{row.idUbicacion}</p>
        </div>
      )
    },
    { key: 'tipoUbicacion', header: 'Tipo', render: (row) => <Badge tone={row.tipoUbicacion === 'ALMACEN' ? 'slate' : 'green'}>{locationTypeLabel(row.tipoUbicacion)}</Badge> },
    { key: 'direccion', header: 'Dirección' },
    { key: 'isActivo', header: 'Estado', render: (row) => <Badge tone={booleanTone(row.isActivo)}>{booleanStatus(row.isActivo)}</Badge> },
    {
      key: 'acciones',
      header: 'Acciones',
      render: (row) => (
        <div className="flex flex-wrap gap-2">
          <Button type="button" variant="secondary" onClick={() => openEditModal(row)} className="px-3 py-2">
            Editar
          </Button>
          <Button
            type="button"
            variant={row.isActivo ? 'danger' : 'secondary'}
            onClick={() => toggleEstado(row)}
            className="px-3 py-2"
          >
            {row.isActivo ? 'Desactivar' : 'Activar'}
          </Button>
        </div>
      )
    }
  ]

  if (loading) return <Loader message="Cargando ubicaciones..." />

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Ubicaciones"
        title="Gestionar almacén central y sucursales"
        description="Administra las ubicaciones operativas del sistema desde una sola vista: almacén central y sucursales. No se eliminan físicamente los registros; se activan o desactivan."
        actions={<Button type="button" onClick={openCreateModal}>Registrar ubicación</Button>}
      />

      {error && <Alert tone="error">{error}</Alert>}
      {success && <Alert tone="success">{success}</Alert>}

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        <Card title="Total ubicaciones" value={resumen.total} description="Almacenes y sucursales" />
        <Card title="Almacenes" value={resumen.almacenes} description="Ubicaciones tipo almacén" />
        <Card title="Sucursales" value={resumen.sucursales} description="Sedes de atención" />
        <Card title="Activas" value={resumen.activas} description="Disponibles para operar" />
        <Card title="Inactivas" value={resumen.inactivas} description="Sin uso operativo" />
      </section>

      <Card>
        <div className="grid gap-4 lg:grid-cols-3">
          <Input
            label="Buscar ubicación"
            placeholder="Nombre, dirección, tipo o ID"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
          <Select label="Tipo" value={tipoFilter} onChange={(event) => setTipoFilter(event.target.value)}>
            <option value="TODOS">Todos</option>
            <option value="ALMACEN">Almacén</option>
            <option value="SUCURSAL">Sucursal</option>
          </Select>
          <Select label="Estado" value={estadoFilter} onChange={(event) => setEstadoFilter(event.target.value)}>
            <option value="TODOS">Todos</option>
            <option value="true">Activas</option>
            <option value="false">Inactivas</option>
          </Select>
        </div>
      </Card>

      <Table
        columns={columns}
        data={filteredUbicaciones}
        keyField="idUbicacion"
        emptyMessage="No hay ubicaciones que coincidan con los filtros."
      />

      <Modal
        title={editingUbicacion ? 'Editar ubicación' : 'Registrar ubicación'}
        description="Completa la información operativa de la ubicación."
        isOpen={modalOpen}
        onClose={closeModal}
        footer={(
          <>
            <Button type="button" variant="secondary" onClick={closeModal} disabled={saving}>Cancelar</Button>
            <Button type="submit" form="ubicacion-form" disabled={saving}>{saving ? 'Guardando...' : 'Guardar'}</Button>
          </>
        )}
      >
        <form id="ubicacion-form" className="space-y-4" onSubmit={handleSubmit}>
          <Input
            label="Nombre"
            placeholder="Ej. Almacén Central o Sucursal Norte"
            value={form.nombreUbicacion}
            onChange={(event) => updateForm('nombreUbicacion', event.target.value)}
            error={formErrors.nombreUbicacion}
          />
          <Select
            label="Tipo de ubicación"
            value={form.tipoUbicacion}
            onChange={(event) => updateForm('tipoUbicacion', event.target.value)}
            error={formErrors.tipoUbicacion}
          >
            <option value="ALMACEN">Almacén</option>
            <option value="SUCURSAL">Sucursal</option>
          </Select>
          <Input
            label="Dirección"
            placeholder="Dirección física de la ubicación"
            value={form.direccion}
            onChange={(event) => updateForm('direccion', event.target.value)}
            error={formErrors.direccion}
          />
          {editingUbicacion && (
            <Select
              label="Estado"
              value={String(form.isActivo)}
              onChange={(event) => updateForm('isActivo', event.target.value === 'true')}
            >
              <option value="true">Activo</option>
              <option value="false">Inactivo</option>
            </Select>
          )}
        </form>
      </Modal>
    </div>
  )
}
