import Button from '@/shared/components/Button'

export default function Modal({ title, description, isOpen, onClose, children, footer, size = 'md' }) {
  if (!isOpen) return null

  const sizeClasses = {
    md: 'max-w-2xl',
    lg: 'max-w-4xl',
    xl: 'max-w-6xl'
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4">
      <div className={`max-h-[90vh] w-full ${sizeClasses[size] || sizeClasses.md} overflow-y-auto rounded-3xl bg-white p-6 shadow-xl`}>
        <div className="flex items-start justify-between gap-4 border-b border-slate-100 pb-4">
          <div>
            <h2 className="text-xl font-black tracking-tight text-slate-950">{title}</h2>
            {description && <p className="mt-1 text-sm text-slate-500">{description}</p>}
          </div>
          <Button type="button" variant="secondary" onClick={onClose} className="px-3 py-2">
            ✕
          </Button>
        </div>

        <div className="py-5">{children}</div>

        {footer && <div className="flex justify-end gap-3 border-t border-slate-100 pt-4">{footer}</div>}
      </div>
    </div>
  )
}
