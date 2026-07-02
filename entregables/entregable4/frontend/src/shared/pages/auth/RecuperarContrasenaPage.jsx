import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import Button from '@/shared/components/Button'
import Input from '@/shared/components/Input'
import { forgotPasswordRequest, resetPasswordRequest, verifyResetCodeRequest } from '@/shared/api/authApi'

const RESEND_SECONDS = 60
const EXPIRE_SECONDS = 180

function formatSeconds(seconds) {
  const safeSeconds = Math.max(0, seconds)
  const minutes = Math.floor(safeSeconds / 60)
  const rest = safeSeconds % 60
  return `${minutes}:${String(rest).padStart(2, '0')}`
}

export default function RecuperarContrasenaPage() {
  const navigate = useNavigate()
  const [step, setStep] = useState('email')
  const [email, setEmail] = useState('')
  const [code, setCode] = useState('')
  const [passwords, setPasswords] = useState({ nuevaContrasena: '', confirmarContrasena: '' })
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [resendSeconds, setResendSeconds] = useState(0)
  const [expireSeconds, setExpireSeconds] = useState(0)

  const canResend = resendSeconds <= 0 && step !== 'email'
  const codeExpired = expireSeconds <= 0 && step !== 'email'

  const title = useMemo(() => {
    if (step === 'email') return 'Recuperar contraseña'
    if (step === 'code') return 'Verifica tu código'
    return 'Crea una nueva contraseña'
  }, [step])

  useEffect(() => {
    if (step === 'email') return undefined

    const interval = window.setInterval(() => {
      setResendSeconds((current) => Math.max(0, current - 1))
      setExpireSeconds((current) => Math.max(0, current - 1))
    }, 1000)

    return () => window.clearInterval(interval)
  }, [step])

  function resetTimers() {
    setResendSeconds(RESEND_SECONDS)
    setExpireSeconds(EXPIRE_SECONDS)
  }

  async function requestCode(event) {
    event?.preventDefault()
    setError('')
    setMessage('')
    setLoading(true)

    try {
      const response = await forgotPasswordRequest({ correoElectronico: email })
      setMessage(response.mensaje || 'Código enviado. Revisa tu correo.')
      setStep('code')
      resetTimers()
    } catch (err) {
      setError(err.message || 'No se pudo enviar el código')
    } finally {
      setLoading(false)
    }
  }

  async function handleVerifyCode(event) {
    event.preventDefault()
    setError('')
    setMessage('')
    setLoading(true)

    try {
      const response = await verifyResetCodeRequest({ correoElectronico: email, codigo: code })
      setMessage(response.mensaje || 'Código verificado correctamente.')
      setStep('password')
    } catch (err) {
      setError(err.message || 'No se pudo verificar el código')
    } finally {
      setLoading(false)
    }
  }

  async function handleResetPassword(event) {
    event.preventDefault()
    setError('')
    setMessage('')

    if (passwords.nuevaContrasena !== passwords.confirmarContrasena) {
      setError('Las contraseñas no coinciden.')
      return
    }

    setLoading(true)
    try {
      const response = await resetPasswordRequest({
        correoElectronico: email,
        codigo: code,
        nuevaContrasena: passwords.nuevaContrasena,
        confirmarContrasena: passwords.confirmarContrasena
      })
      setMessage(response.mensaje || 'Contraseña actualizada correctamente.')
      window.setTimeout(() => navigate('/login'), 1200)
    } catch (err) {
      setError(err.message || 'No se pudo actualizar la contraseña')
    } finally {
      setLoading(false)
    }
  }

  async function handleResend() {
    if (!canResend) return
    await requestCode()
  }

  function updatePassword(event) {
    const { name, value } = event.target
    setPasswords((current) => ({ ...current, [name]: value }))
  }

  return (
    <main className="min-h-screen bg-slate-950 px-4 py-10 text-white">
      <div className="mx-auto flex min-h-[calc(100vh-5rem)] max-w-2xl items-center justify-center">
        <section className="w-full rounded-3xl bg-white p-6 text-slate-950 shadow-2xl sm:p-8">
          <div className="mb-6">
            <p className="text-sm font-bold uppercase tracking-[0.25em] text-slate-400">Codex Venta</p>
            <h1 className="mt-3 text-2xl font-black">{title}</h1>
            <p className="mt-1 text-sm text-slate-500">
              Recibirás un código temporal en el correo registrado. El código vence en 3 minutos.
            </p>
          </div>

          {message && (
            <div className="mb-4 rounded-2xl border border-green-200 bg-green-50 px-4 py-3 text-sm font-medium text-green-700">
              {message}
            </div>
          )}

          {error && (
            <div className="mb-4 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700">
              {error}
            </div>
          )}

          {step === 'email' && (
            <form className="space-y-4" onSubmit={requestCode}>
              <Input
                label="Correo electrónico"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                autoComplete="email"
                placeholder="usuario@correo.com"
                required
              />
              <Button className="w-full" type="submit" disabled={loading}>
                {loading ? 'Enviando...' : 'Enviar código'}
              </Button>
            </form>
          )}

          {step === 'code' && (
            <form className="space-y-4" onSubmit={handleVerifyCode}>
              <Input
                label="Código de verificación"
                value={code}
                onChange={(event) => setCode(event.target.value.replace(/\D/g, '').slice(0, 6))}
                inputMode="numeric"
                placeholder="000000"
                required
              />

              <div className="rounded-2xl bg-slate-50 p-4 text-sm text-slate-600">
                <p>Código válido por: <strong>{formatSeconds(expireSeconds)}</strong></p>
                {codeExpired && <p className="mt-1 font-semibold text-red-600">El código venció. Solicita un reenvío.</p>}
              </div>

              <div className="grid gap-3 sm:grid-cols-2">
                <Button type="submit" disabled={loading || code.length !== 6 || codeExpired}>
                  {loading ? 'Verificando...' : 'Verificar código'}
                </Button>
                <Button type="button" variant="secondary" onClick={handleResend} disabled={loading || !canResend}>
                  {canResend ? 'Reenviar código' : `Reenviar en ${resendSeconds}s`}
                </Button>
              </div>
            </form>
          )}

          {step === 'password' && (
            <form className="space-y-4" onSubmit={handleResetPassword}>
              <Input
                label="Nueva contraseña"
                type="password"
                name="nuevaContrasena"
                value={passwords.nuevaContrasena}
                onChange={updatePassword}
                autoComplete="new-password"
                minLength={8}
                required
              />
              <Input
                label="Confirmar contraseña"
                type="password"
                name="confirmarContrasena"
                value={passwords.confirmarContrasena}
                onChange={updatePassword}
                autoComplete="new-password"
                minLength={8}
                required
              />
              <div className="grid gap-3 sm:grid-cols-2">
                <Button type="submit" disabled={loading || codeExpired}>
                  {loading ? 'Guardando...' : 'Cambiar contraseña'}
                </Button>
                <Button type="button" variant="secondary" onClick={handleResend} disabled={loading || !canResend}>
                  {canResend ? 'Reenviar código' : `Reenviar en ${resendSeconds}s`}
                </Button>
              </div>
            </form>
          )}

          <div className="mt-6 text-center text-sm">
            <Link to="/login" className="font-semibold text-slate-700 underline-offset-4 hover:underline">
              Volver al inicio de sesión
            </Link>
          </div>
        </section>
      </div>
    </main>
  )
}
