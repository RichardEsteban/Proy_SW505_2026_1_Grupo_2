export default function Alert({ tone = 'info', children }) {
  const tones = {
    info: 'border-slate-200 bg-white text-slate-700',
    error: 'border-red-200 bg-red-50 text-red-700',
    success: 'border-emerald-200 bg-emerald-50 text-emerald-700',
    warning: 'border-amber-200 bg-amber-50 text-amber-800'
  }

  return (
    <div className={`rounded-2xl border px-4 py-3 text-sm font-medium ${tones[tone] || tones.info}`}>
      {children}
    </div>
  )
}
