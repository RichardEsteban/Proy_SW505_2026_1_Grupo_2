export default function PageHeader({ eyebrow = 'Módulo', title, description, actions, action }) {
  const headerActions = actions || action
  return (
    <section className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
      <div>
        <p className="text-sm font-semibold text-slate-500">{eyebrow}</p>
        <h1 className="mt-1 text-3xl font-black tracking-tight text-slate-950">{title}</h1>
        {description && <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">{description}</p>}
      </div>
      {headerActions && <div className="flex flex-wrap gap-2">{headerActions}</div>}
    </section>
  )
}
