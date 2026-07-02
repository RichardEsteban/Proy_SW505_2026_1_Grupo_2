import { Link } from 'react-router-dom'
import Button from '@/shared/components/Button'

export default function NotFoundPage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <section className="max-w-md rounded-3xl border border-slate-200 bg-white p-8 text-center shadow-sm">
        <p className="text-sm font-bold uppercase tracking-[0.3em] text-slate-400">404</p>
        <h1 className="mt-3 text-3xl font-black text-slate-950">Página no encontrada</h1>
        <p className="mt-3 text-sm leading-6 text-slate-600">La ruta que intentaste abrir no existe.</p>
        <Link to="/dashboard" className="mt-6 inline-block">
          <Button>Volver al dashboard</Button>
        </Link>
      </section>
    </main>
  )
}
