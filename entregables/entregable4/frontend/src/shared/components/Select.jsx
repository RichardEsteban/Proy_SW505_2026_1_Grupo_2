export default function Select({ label, error, className = '', children, ...props }) {
  return (
    <label className="block space-y-1.5">
      {label && <span className="text-sm font-medium text-slate-700">{label}</span>}
      <select
        className={`w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm text-slate-900 outline-none transition focus:border-slate-400 focus:ring-4 focus:ring-slate-100 ${error ? 'border-red-300 focus:border-red-400 focus:ring-red-100' : ''} ${className}`}
        {...props}
      >
        {children}
      </select>
      {error && <span className="text-xs font-medium text-red-600">{error}</span>}
    </label>
  )
}
