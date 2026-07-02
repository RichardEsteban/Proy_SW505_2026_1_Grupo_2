export default function Card({ title, value, description, children }) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      {title && <p className="text-sm font-medium text-slate-500">{title}</p>}
      {value !== undefined && <p className="mt-2 text-3xl font-bold tracking-tight text-slate-950">{value}</p>}
      {description && <p className="mt-1 text-sm text-slate-500">{description}</p>}
      {children}
    </section>
  )
}
