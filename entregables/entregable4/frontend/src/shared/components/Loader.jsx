export default function Loader({ message = 'Cargando...' }) {
  return (
    <div className="flex min-h-[240px] items-center justify-center">
      <div className="rounded-2xl border border-slate-200 bg-white px-6 py-5 text-center shadow-sm">
        <div className="mx-auto h-8 w-8 animate-spin rounded-full border-4 border-slate-200 border-t-slate-900" />
        <p className="mt-3 text-sm font-medium text-slate-600">{message}</p>
      </div>
    </div>
  )
}
