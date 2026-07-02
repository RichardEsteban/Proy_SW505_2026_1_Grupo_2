import { NavLink } from 'react-router-dom'
import { useAuth } from '@/shared/auth/AuthContext'
import { getMenuForRole, ROLE_VIEW_LABELS } from '@/shared/utils/roleViews'

export default function Sidebar() {
  const { usuario } = useAuth()
  const role = usuario?.rol
  const menuItems = getMenuForRole(role)

  return (
    <aside className="hidden min-h-screen w-72 border-r border-slate-200 bg-white px-4 py-5 lg:block">
      <div className="mb-8 px-3">
        <p className="text-xs font-bold uppercase tracking-[0.25em] text-slate-400">Sistema</p>
        <h1 className="mt-2 text-xl font-black text-slate-950">MYPE POS</h1>
        <p className="mt-2 rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
          {ROLE_VIEW_LABELS[role] || role || 'Usuario'}
        </p>
      </div>

      <nav className="space-y-1">
        {menuItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex rounded-xl px-3 py-2.5 text-sm font-semibold transition ${
                isActive
                  ? 'bg-slate-900 text-white shadow-sm'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-950'
              }`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
