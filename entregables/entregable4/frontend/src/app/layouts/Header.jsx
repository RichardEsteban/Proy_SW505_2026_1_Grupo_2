import Button from '@/shared/components/Button'
import Badge from '@/shared/components/Badge'
import { useAuth } from '@/shared/auth/AuthContext'
import { ROLE_VIEW_LABELS } from '@/shared/utils/roleViews'

export default function Header() {
  const { usuario, logout } = useAuth()

  return (
    <header className="sticky top-0 z-10 border-b border-slate-200 bg-white/90 px-4 py-3 backdrop-blur lg:px-8">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-sm font-semibold text-slate-500">Bienvenido</p>
          <h2 className="text-lg font-bold text-slate-950">{usuario?.correoElectronico}</h2>
        </div>

        <div className="flex items-center gap-3">
          <div className="hidden text-right sm:block">
            <Badge>{ROLE_VIEW_LABELS[usuario?.rol] || usuario?.rol}</Badge>
            <p className="mt-1 text-xs text-slate-500">{usuario?.ubicacion}</p>
          </div>
          <Button variant="secondary" onClick={logout}>Salir</Button>
        </div>
      </div>
    </header>
  )
}
