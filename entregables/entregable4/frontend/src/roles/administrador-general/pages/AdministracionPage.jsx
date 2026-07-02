import { useEffect, useMemo, useState } from 'react'
import { actualizarEmpresa, obtenerEmpresa } from '@/shared/api/empresaApi'
import { actualizarUbicacion, crearUbicacion, listarUbicaciones } from '@/shared/api/ubicacionApi'
import { actualizarUsuario, cambiarMiContrasena, crearUsuario, listarRoles, listarUsuarios } from '@/shared/api/usuarioApi'
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
import {
  booleanStatus,
  booleanTone,
  canManageAdmin,
  formatTemporaryPassword,
  getApiErrorMessage,
  locationTypeLabel,
  normalizeNumber,
  roleLabel
} from '@/shared/utils/admin'

const tabs = [
  { id: 'usuarios', label: 'Usuarios' },
  { id: 'ubicaciones', label: 'Ubicaciones' },
  { id: 'empresa', label: 'Empresa' },
  { id: 'seguridad', label: 'Mi contraseña' }
]

const emptyUsuarioForm = {
  correoElectronico: '',
  contrasenaTemporal: '',
  idRol: '',
  idUbicacion: '',
  isActivo: true
}

const emptyUbicacionForm = {
  nombreUbicacion: '',
  tipoUbicacion: 'SUCURSAL',
  direccion: '',
  isActivo: true
}

const emptyEmpresaForm = {
  nombreEmpresa: '',
  timer_revision_minutos: '60',
  igv_porcentaje: '18.00',
  moneda: 'PEN'
}

const emptyPasswordForm = {
  contrasenaActual: '',
  contrasenaNueva: '',
  confirmarContrasena: ''
}

function buildUsuarioPayload(form, isEdit) {
  const payload = {
    correoElectronico: form.correoElectronico.trim(),
    idRol: Number(form.idRol),
    idUbicacion: Number(form.idUbicacion)
  }

  if (isEdit) {
    payload.isActivo = form.isActivo
  } else {
    payload.contrasenaTemporal = form.contrasenaTemporal
  }

  return payload
}

function buildUbicacionPayload(form, isEdit) {
  const payload = {
    nombreUbicacion: form.nombreUbicacion.trim(),
    tipoUbicacion: form.tipoUbicacion,
    direccion: form.direccion.trim()
  }

  if (isEdit) payload.isActivo = form.isActivo

  return payload
}

function sanitizeIntegerRange(value, min, max) {
  if (value === '') return ''
  const number = Number(value)
  if (!Number.isFinite(number)) return ''
  if (number < min) return String(min)
  if (number > max) return String(max)
  return String(Math.floor(number))
}

function sanitizeDecimalRange(value, min, max) {
  if (value === '') return ''
  const text = String(value).replace(/-/g, '')
  const number = Number(text)
  if (!Number.isFinite(number)) return ''
  if (number < min) return String(min)
  if (number > max) return String(max)
  return text
}

function buildEmpresaPayload(form) {
  return {
    nombreEmpresa: form.nombreEmpresa.trim(),
    timer_revision_minutos: Number(form.timer_revision_minutos),
    igv_porcentaje: Number(form.igv_porcentaje),
    moneda: form.moneda.trim().toUpperCase()
  }
}

function TabButton({ active, children, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded-xl px-4 py-2.5 text-sm font-semibold transition ${
        active
          ? 'bg-slate-900 text-white shadow-sm'
          : 'bg-white text-slate-600 ring-1 ring-slate-200 hover:bg-slate-50 hover:text-slate-950'
      }`}
    >
      {children}
    </button>
  )
}

export default function AdministracionPage() {
  const { usuario } = useAuth()
  const canManage = canManageAdmin(usuario?.rol)
  const [activeTab, setActiveTab] = useState('usuarios')
  const [usuarios, setUsuarios] = useState([])
  const [roles, setRoles] = useState([])
  const [ubicaciones, setUbicaciones] = useState([])
  const [empresa, setEmpresa] = useState(null)
  const [searchUsuarios, setSearchUsuarios] = useState('')
  const [searchUbicaciones, setSearchUbicaciones] = useState('')
  const [showInactiveUsers, setShowInactiveUsers] = useState(true)
  const [showInactiveLocations, setShowInactiveLocations] = useState(true)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const [isUsuarioModalOpen, setIsUsuarioModalOpen] = useState(false)
  const [editingUsuario, setEditingUsuario] = useState(null)
  const [usuarioForm, setUsuarioForm] = useState(emptyUsuarioForm)

  const [isUbicacionModalOpen, setIsUbicacionModalOpen] = useState(false)
  const [editingUbicacion, setEditingUbicacion] = useState(null)
  const [ubicacionForm, setUbicacionForm] = useState(emptyUbicacionForm)

  const [empresaForm, setEmpresaForm] = useState(emptyEmpresaForm)
  const [passwordForm, setPasswordForm] = useState(emptyPasswordForm)

  async function loadAdminData() {
    if (!canManage) {
      setLoading(false)
      return
    }

    setLoading(true)
    setError('')

    try {
      const [usuariosData, rolesData, ubicacionesData, empresaData] = await Promise.all([
        listarUsuarios({ incluirInactivos: showInactiveUsers }),
        listarRoles(),
        listarUbicaciones({ incluirInactivas: showInactiveLocations }),
        obtenerEmpresa()
      ])

      setUsuarios(usuariosData)
      setRoles(rolesData)
      setUbicaciones(ubicacionesData)
      setEmpresa(empresaData)
      setEmpresaForm({
        nombreEmpresa: empresaData.nombreEmpresa || '',
        timer_revision_minutos: normalizeNumber(empresaData.timer_revision_minutos),
        igv_porcentaje: normalizeNumber(empresaData.igv_porcentaje),
        moneda: empresaData.moneda || 'PEN'
      })
    } catch (err) {
      setError(getApiErrorMessage(err, 'No se pudo cargar la administración'))
    } finally {
      setLoading(false)
    }
  }

  async function loadUsuarios() {
    const data = await listarUsuarios({ incluirInactivos: showInactiveUsers })
    setUsuarios(data)
  }

  async function loadUbicaciones() {
    const data = await listarUbicaciones({ incluirInactivas: showInactiveLocations })
    setUbicaciones(data)
  }

  useEffect(() => {
    loadAdminData()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    if (!canManage || loading) return

    loadUsuarios().catch((err) => setError(getApiErrorMessage(err, 'No se pudieron cargar los usuarios')))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [showInactiveUsers])

  useEffect(() => {
    if (!canManage || loading) return

    loadUbicaciones().catch((err) => setError(getApiErrorMessage(err, 'No se pudieron cargar las ubicaciones')))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [showInactiveLocations])

  const filteredUsuarios = useMemo(() => {
    const term = searchUsuarios.trim().toLowerCase()
    if (!term) return usuarios

    return usuarios.filter((item) => (
      item.correoElectronico.toLowerCase().includes(term) ||
      item.rol.toLowerCase().includes(term) ||
      item.ubicacion.toLowerCase().includes(term) ||
      String(item.idUsuario).includes(term)
    ))
  }, [usuarios, searchUsuarios])

  const filteredUbicaciones = useMemo(() => {
    const term = searchUbicaciones.trim().toLowerCase()
    if (!term) return ubicaciones

    return ubicaciones.filter((item) => (
      item.nombreUbicacion.toLowerCase().includes(term) ||
      item.tipoUbicacion.toLowerCase().includes(term) ||
      item.direccion.toLowerCase().includes(term) ||
      String(item.idUbicacion).includes(term)
    ))
  }, [ubicaciones, searchUbicaciones])

  const metrics = useMemo(() => {
    const activeUsers = usuarios.filter((item) => item.isActivo).length
    const activeLocations = ubicaciones.filter((item) => item.isActivo).length
    const warehouses = ubicaciones.filter((item) => item.tipoUbicacion === 'ALMACEN').length
    const branches = ubicaciones.filter((item) => item.tipoUbicacion === 'SUCURSAL').length

    return { activeUsers, activeLocations, warehouses, branches }
  }, [usuarios, ubicaciones])

  function resetMessages() {
    setError('')
    setSuccess('')
  }

  function openCreateUsuario() {
    resetMessages()
    setEditingUsuario(null)
    setUsuarioForm({
      ...emptyUsuarioForm,
      idRol: roles[0]?.idRol ? String(roles[0].idRol) : '',
      idUbicacion: ubicaciones[0]?.idUbicacion ? String(ubicaciones[0].idUbicacion) : ''
    })
    setIsUsuarioModalOpen(true)
  }

  function openEditUsuario(item) {
    resetMessages()
    setEditingUsuario(item)
    setUsuarioForm({
      correoElectronico: item.correoElectronico,
      contrasenaTemporal: '',
      idRol: String(item.idRol),
      idUbicacion: String(item.idUbicacion),
      isActivo: item.isActivo
    })
    setIsUsuarioModalOpen(true)
  }

  function handleUsuarioChange(event) {
    const { name, value, type, checked } = event.target
    setUsuarioForm((prev) => ({ ...prev, [name]: type === 'checkbox' ? checked : value }))
  }

  async function handleUsuarioSubmit(event) {
    event.preventDefault()
    setSaving(true)
    resetMessages()

    try {
      const payload = buildUsuarioPayload(usuarioForm, Boolean(editingUsuario))

      if (editingUsuario) {
        await actualizarUsuario(editingUsuario.idUsuario, payload)
        setSuccess('Usuario actualizado correctamente')
      } else {
        await crearUsuario(payload)
        setSuccess('Usuario creado correctamente')
      }

      setIsUsuarioModalOpen(false)
      await loadUsuarios()
    } catch (err) {
      setError(getApiErrorMessage(err, 'No se pudo guardar el usuario'))
    } finally {
      setSaving(false)
    }
  }

  async function toggleUsuarioStatus(item) {
    setSaving(true)
    resetMessages()

    try {
      await actualizarUsuario(item.idUsuario, { isActivo: !item.isActivo })
      setSuccess(`Usuario ${!item.isActivo ? 'activado' : 'desactivado'} correctamente`)
      await loadUsuarios()
    } catch (err) {
      setError(getApiErrorMessage(err, 'No se pudo cambiar el estado del usuario'))
    } finally {
      setSaving(false)
    }
  }

  function openCreateUbicacion() {
    resetMessages()
    setEditingUbicacion(null)
    setUbicacionForm(emptyUbicacionForm)
    setIsUbicacionModalOpen(true)
  }

  function openEditUbicacion(item) {
    resetMessages()
    setEditingUbicacion(item)
    setUbicacionForm({
      nombreUbicacion: item.nombreUbicacion,
      tipoUbicacion: item.tipoUbicacion,
      direccion: item.direccion,
      isActivo: item.isActivo
    })
    setIsUbicacionModalOpen(true)
  }

  function handleUbicacionChange(event) {
    const { name, value, type, checked } = event.target
    setUbicacionForm((prev) => ({ ...prev, [name]: type === 'checkbox' ? checked : value }))
  }

  async function handleUbicacionSubmit(event) {
    event.preventDefault()
    setSaving(true)
    resetMessages()

    try {
      const payload = buildUbicacionPayload(ubicacionForm, Boolean(editingUbicacion))

      if (editingUbicacion) {
        await actualizarUbicacion(editingUbicacion.idUbicacion, payload)
        setSuccess('Ubicación actualizada correctamente')
      } else {
        await crearUbicacion(payload)
        setSuccess('Ubicación creada correctamente')
      }

      setIsUbicacionModalOpen(false)
      await loadUbicaciones()
    } catch (err) {
      setError(getApiErrorMessage(err, 'No se pudo guardar la ubicación'))
    } finally {
      setSaving(false)
    }
  }

  async function toggleUbicacionStatus(item) {
    setSaving(true)
    resetMessages()

    try {
      await actualizarUbicacion(item.idUbicacion, { isActivo: !item.isActivo })
      setSuccess(`Ubicación ${!item.isActivo ? 'activada' : 'desactivada'} correctamente`)
      await loadUbicaciones()
    } catch (err) {
      setError(getApiErrorMessage(err, 'No se pudo cambiar el estado de la ubicación'))
    } finally {
      setSaving(false)
    }
  }

  function handleEmpresaChange(event) {
    const { name, value } = event.target
    let nextValue = value

    if (name === 'timer_revision_minutos') nextValue = sanitizeIntegerRange(value, 1, 1440)
    if (name === 'igv_porcentaje') nextValue = sanitizeDecimalRange(value, 0, 100)

    setEmpresaForm((prev) => ({ ...prev, [name]: nextValue }))
  }

  async function handleEmpresaSubmit(event) {
    event.preventDefault()
    setSaving(true)
    resetMessages()

    try {
      const data = await actualizarEmpresa(buildEmpresaPayload(empresaForm))
      setEmpresa(data)
      setEmpresaForm({
        nombreEmpresa: data.nombreEmpresa || '',
        timer_revision_minutos: normalizeNumber(data.timer_revision_minutos),
        igv_porcentaje: normalizeNumber(data.igv_porcentaje),
        moneda: data.moneda || 'PEN'
      })
      setSuccess('Configuración de empresa actualizada correctamente')
    } catch (err) {
      setError(getApiErrorMessage(err, 'No se pudo actualizar la empresa'))
    } finally {
      setSaving(false)
    }
  }

  function handlePasswordChange(event) {
    const { name, value } = event.target
    setPasswordForm((prev) => ({ ...prev, [name]: value }))
  }

  async function handlePasswordSubmit(event) {
    event.preventDefault()
    setSaving(true)
    resetMessages()

    if (passwordForm.contrasenaNueva !== passwordForm.confirmarContrasena) {
      setSaving(false)
      setError('La confirmación no coincide con la nueva contraseña')
      return
    }

    try {
      await cambiarMiContrasena({
        contrasenaActual: passwordForm.contrasenaActual,
        contrasenaNueva: passwordForm.contrasenaNueva
      })
      setPasswordForm(emptyPasswordForm)
      setSuccess('Contraseña actualizada correctamente')
    } catch (err) {
      setError(getApiErrorMessage(err, 'No se pudo cambiar la contraseña'))
    } finally {
      setSaving(false)
    }
  }

  const usuarioColumns = [
    { key: 'idUsuario', header: 'ID', render: (row) => <span className="font-semibold text-slate-900">#{row.idUsuario}</span> },
    { key: 'correoElectronico', header: 'Correo', render: (row) => <span className="font-semibold text-slate-900">{row.correoElectronico}</span> },
    { key: 'rol', header: 'Rol', render: (row) => roleLabel(row.rol) },
    { key: 'ubicacion', header: 'Ubicación' },
    { key: 'tipoUbicacion', header: 'Tipo', render: (row) => locationTypeLabel(row.tipoUbicacion) },
    { key: 'isContrasenaTemporal', header: 'Contraseña', render: (row) => <Badge tone={row.isContrasenaTemporal ? 'amber' : 'green'}>{formatTemporaryPassword(row.isContrasenaTemporal)}</Badge> },
    { key: 'isActivo', header: 'Estado', render: (row) => <Badge tone={booleanTone(row.isActivo)}>{booleanStatus(row.isActivo)}</Badge> },
    {
      key: 'acciones',
      header: 'Acciones',
      render: (row) => (
        <div className="flex flex-wrap gap-2">
          <Button type="button" variant="secondary" className="px-3 py-2" onClick={() => openEditUsuario(row)}>
            Editar
          </Button>
          <Button
            type="button"
            variant={row.isActivo ? 'danger' : 'secondary'}
            className="px-3 py-2"
            disabled={saving}
            onClick={() => toggleUsuarioStatus(row)}
          >
            {row.isActivo ? 'Desactivar' : 'Activar'}
          </Button>
        </div>
      )
    }
  ]

  const ubicacionColumns = [
    { key: 'idUbicacion', header: 'ID', render: (row) => <span className="font-semibold text-slate-900">#{row.idUbicacion}</span> },
    { key: 'nombreUbicacion', header: 'Ubicación', render: (row) => <span className="font-semibold text-slate-900">{row.nombreUbicacion}</span> },
    { key: 'tipoUbicacion', header: 'Tipo', render: (row) => <Badge tone={row.tipoUbicacion === 'ALMACEN' ? 'slate' : 'green'}>{locationTypeLabel(row.tipoUbicacion)}</Badge> },
    { key: 'direccion', header: 'Dirección' },
    { key: 'isActivo', header: 'Estado', render: (row) => <Badge tone={booleanTone(row.isActivo)}>{booleanStatus(row.isActivo)}</Badge> },
    {
      key: 'acciones',
      header: 'Acciones',
      render: (row) => (
        <div className="flex flex-wrap gap-2">
          <Button type="button" variant="secondary" className="px-3 py-2" onClick={() => openEditUbicacion(row)}>
            Editar
          </Button>
          <Button
            type="button"
            variant={row.isActivo ? 'danger' : 'secondary'}
            className="px-3 py-2"
            disabled={saving}
            onClick={() => toggleUbicacionStatus(row)}
          >
            {row.isActivo ? 'Desactivar' : 'Activar'}
          </Button>
        </div>
      )
    }
  ]

  if (!canManage) {
    return (
      <div className="space-y-6">
        <PageHeader
          eyebrow="Administración"
          title="Acceso restringido"
          description="Este módulo está disponible solo para usuarios administradores."
        />
        <Alert tone="warning">Tu rol actual no tiene permiso para administrar usuarios, ubicaciones ni empresa.</Alert>
      </div>
    )
  }

  if (loading) return <Loader message="Cargando administración..." />

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Administración"
        title="Usuarios, ubicaciones y empresa"
        description="Gestiona usuarios del sistema, roles asignados, sedes, almacenes y parámetros generales de la empresa."
      />

      {error && <Alert tone="error">{error}</Alert>}
      {success && <Alert tone="success">{success}</Alert>}

      <div className="grid gap-4 md:grid-cols-4">
        <Card title="Usuarios activos" value={metrics.activeUsers} description={`${usuarios.length} usuarios en total`} />
        <Card title="Ubicaciones activas" value={metrics.activeLocations} description={`${ubicaciones.length} ubicaciones en total`} />
        <Card title="Almacenes" value={metrics.warehouses} description="Ubicaciones tipo almacén" />
        <Card title="Sucursales" value={metrics.branches} description="Puntos de venta o atención" />
      </div>

      <div className="flex flex-wrap gap-2">
        {tabs.map((tab) => (
          <TabButton key={tab.id} active={activeTab === tab.id} onClick={() => setActiveTab(tab.id)}>
            {tab.label}
          </TabButton>
        ))}
      </div>

      {activeTab === 'usuarios' && (
        <section className="space-y-4">
          <Card>
            <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <Input
                label="Buscar usuario"
                placeholder="Correo, rol, ubicación o ID"
                value={searchUsuarios}
                onChange={(event) => setSearchUsuarios(event.target.value)}
                className="md:w-96"
              />
              <div className="flex flex-wrap items-center gap-3">
                <label className="flex items-center gap-2 text-sm font-medium text-slate-700">
                  <input
                    type="checkbox"
                    checked={showInactiveUsers}
                    onChange={(event) => setShowInactiveUsers(event.target.checked)}
                    className="h-4 w-4 rounded border-slate-300"
                  />
                  Mostrar inactivos
                </label>
                <Button type="button" onClick={openCreateUsuario}>Nuevo usuario</Button>
              </div>
            </div>
          </Card>
          <Table columns={usuarioColumns} data={filteredUsuarios} keyField="idUsuario" emptyMessage="No hay usuarios para mostrar." />
        </section>
      )}

      {activeTab === 'ubicaciones' && (
        <section className="space-y-4">
          <Card>
            <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <Input
                label="Buscar ubicación"
                placeholder="Nombre, tipo, dirección o ID"
                value={searchUbicaciones}
                onChange={(event) => setSearchUbicaciones(event.target.value)}
                className="md:w-96"
              />
              <div className="flex flex-wrap items-center gap-3">
                <label className="flex items-center gap-2 text-sm font-medium text-slate-700">
                  <input
                    type="checkbox"
                    checked={showInactiveLocations}
                    onChange={(event) => setShowInactiveLocations(event.target.checked)}
                    className="h-4 w-4 rounded border-slate-300"
                  />
                  Mostrar inactivas
                </label>
                <Button type="button" onClick={openCreateUbicacion}>Nueva ubicación</Button>
              </div>
            </div>
          </Card>
          <Table columns={ubicacionColumns} data={filteredUbicaciones} keyField="idUbicacion" emptyMessage="No hay ubicaciones para mostrar." />
        </section>
      )}

      {activeTab === 'empresa' && (
        <section className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
          <Card>
            <form className="space-y-4" onSubmit={handleEmpresaSubmit}>
              <div>
                <h2 className="text-lg font-black text-slate-950">Configuración de empresa</h2>
                <p className="mt-1 text-sm text-slate-500">Estos valores afectan impuestos, moneda y el tiempo de revisión de reposiciones.</p>
              </div>
              <Input label="Nombre de empresa" name="nombreEmpresa" value={empresaForm.nombreEmpresa} onChange={handleEmpresaChange} required minLength={2} maxLength={150} />
              <div className="grid gap-4 md:grid-cols-3">
                <Input label="Timer revisión (min)" name="timer_revision_minutos" type="number" min="1" max="1440" value={empresaForm.timer_revision_minutos} onChange={handleEmpresaChange} required />
                <Input label="IGV (%)" name="igv_porcentaje" type="number" min="0" max="100" step="0.01" value={empresaForm.igv_porcentaje} onChange={handleEmpresaChange} required />
                <Input label="Moneda" name="moneda" value={empresaForm.moneda} onChange={handleEmpresaChange} required minLength={3} maxLength={3} />
              </div>
              <div className="flex justify-end">
                <Button type="submit" disabled={saving}>Guardar empresa</Button>
              </div>
            </form>
          </Card>

          <Card>
            <h2 className="text-lg font-black text-slate-950">Estado actual</h2>
            <dl className="mt-4 space-y-3 text-sm">
              <div className="flex justify-between gap-4 border-b border-slate-100 pb-3">
                <dt className="font-medium text-slate-500">Empresa</dt>
                <dd className="font-semibold text-slate-900">{empresa?.nombreEmpresa}</dd>
              </div>
              <div className="flex justify-between gap-4 border-b border-slate-100 pb-3">
                <dt className="font-medium text-slate-500">Inicializado</dt>
                <dd><Badge tone={empresa?.isInicializado ? 'green' : 'amber'}>{empresa?.isInicializado ? 'Sí' : 'No'}</Badge></dd>
              </div>
              <div className="flex justify-between gap-4 border-b border-slate-100 pb-3">
                <dt className="font-medium text-slate-500">Timer revisión</dt>
                <dd className="font-semibold text-slate-900">{empresa?.timer_revision_minutos} min</dd>
              </div>
              <div className="flex justify-between gap-4 border-b border-slate-100 pb-3">
                <dt className="font-medium text-slate-500">IGV</dt>
                <dd className="font-semibold text-slate-900">{Number(empresa?.igv_porcentaje || 0).toFixed(2)}%</dd>
              </div>
              <div className="flex justify-between gap-4">
                <dt className="font-medium text-slate-500">Moneda</dt>
                <dd className="font-semibold text-slate-900">{empresa?.moneda}</dd>
              </div>
            </dl>
          </Card>
        </section>
      )}

      {activeTab === 'seguridad' && (
        <section className="max-w-2xl">
          <Card>
            <form className="space-y-4" onSubmit={handlePasswordSubmit}>
              <div>
                <h2 className="text-lg font-black text-slate-950">Cambiar mi contraseña</h2>
                <p className="mt-1 text-sm text-slate-500">Este cambio afecta únicamente al usuario con sesión iniciada.</p>
              </div>
              <Input label="Contraseña actual" name="contrasenaActual" type="password" value={passwordForm.contrasenaActual} onChange={handlePasswordChange} required />
              <Input label="Nueva contraseña" name="contrasenaNueva" type="password" value={passwordForm.contrasenaNueva} onChange={handlePasswordChange} required minLength={8} maxLength={72} />
              <Input label="Confirmar nueva contraseña" name="confirmarContrasena" type="password" value={passwordForm.confirmarContrasena} onChange={handlePasswordChange} required minLength={8} maxLength={72} />
              <div className="flex justify-end">
                <Button type="submit" disabled={saving}>Cambiar contraseña</Button>
              </div>
            </form>
          </Card>
        </section>
      )}

      <Modal
        title={editingUsuario ? 'Editar usuario' : 'Nuevo usuario'}
        description="Asigna rol y ubicación para controlar permisos y alcance operativo."
        isOpen={isUsuarioModalOpen}
        onClose={() => setIsUsuarioModalOpen(false)}
        footer={(
          <>
            <Button type="button" variant="secondary" onClick={() => setIsUsuarioModalOpen(false)}>Cancelar</Button>
            <Button type="submit" form="usuario-form" disabled={saving}>{editingUsuario ? 'Guardar cambios' : 'Crear usuario'}</Button>
          </>
        )}
      >
        <form id="usuario-form" className="space-y-4" onSubmit={handleUsuarioSubmit}>
          <Input label="Correo electrónico" name="correoElectronico" type="email" value={usuarioForm.correoElectronico} onChange={handleUsuarioChange} required />
          {!editingUsuario && (
            <Input label="Contraseña temporal" name="contrasenaTemporal" type="password" value={usuarioForm.contrasenaTemporal} onChange={handleUsuarioChange} required minLength={8} maxLength={72} />
          )}
          <div className="grid gap-4 md:grid-cols-2">
            <Select label="Rol" name="idRol" value={usuarioForm.idRol} onChange={handleUsuarioChange} required>
              <option value="">Seleccionar rol</option>
              {roles.map((rol) => <option key={rol.idRol} value={rol.idRol}>{roleLabel(rol.nombreRol)}</option>)}
            </Select>
            <Select label="Ubicación" name="idUbicacion" value={usuarioForm.idUbicacion} onChange={handleUsuarioChange} required>
              <option value="">Seleccionar ubicación</option>
              {ubicaciones.map((item) => (
                <option key={item.idUbicacion} value={item.idUbicacion}>
                  {item.nombreUbicacion} · {locationTypeLabel(item.tipoUbicacion)}
                </option>
              ))}
            </Select>
          </div>
          {editingUsuario && (
            <label className="flex items-center gap-2 text-sm font-medium text-slate-700">
              <input type="checkbox" name="isActivo" checked={usuarioForm.isActivo} onChange={handleUsuarioChange} className="h-4 w-4 rounded border-slate-300" />
              Usuario activo
            </label>
          )}
        </form>
      </Modal>

      <Modal
        title={editingUbicacion ? 'Editar ubicación' : 'Nueva ubicación'}
        description="Registra almacenes y sucursales para controlar stock, ventas y reposiciones."
        isOpen={isUbicacionModalOpen}
        onClose={() => setIsUbicacionModalOpen(false)}
        footer={(
          <>
            <Button type="button" variant="secondary" onClick={() => setIsUbicacionModalOpen(false)}>Cancelar</Button>
            <Button type="submit" form="ubicacion-form" disabled={saving}>{editingUbicacion ? 'Guardar cambios' : 'Crear ubicación'}</Button>
          </>
        )}
      >
        <form id="ubicacion-form" className="space-y-4" onSubmit={handleUbicacionSubmit}>
          <Input label="Nombre de ubicación" name="nombreUbicacion" value={ubicacionForm.nombreUbicacion} onChange={handleUbicacionChange} required minLength={2} maxLength={150} />
          <Select label="Tipo de ubicación" name="tipoUbicacion" value={ubicacionForm.tipoUbicacion} onChange={handleUbicacionChange} required>
            <option value="ALMACEN">Almacén</option>
            <option value="SUCURSAL">Sucursal</option>
          </Select>
          <Input label="Dirección" name="direccion" value={ubicacionForm.direccion} onChange={handleUbicacionChange} required minLength={2} maxLength={255} />
          {editingUbicacion && (
            <label className="flex items-center gap-2 text-sm font-medium text-slate-700">
              <input type="checkbox" name="isActivo" checked={ubicacionForm.isActivo} onChange={handleUbicacionChange} className="h-4 w-4 rounded border-slate-300" />
              Ubicación activa
            </label>
          )}
        </form>
      </Modal>
    </div>
  )
}
