export default function Button({ children, className = '', variant = 'primary', as: Component = 'button', ...props }) {
  const variants = {
    primary: 'bg-slate-900 text-white hover:bg-slate-800 focus:ring-slate-400',
    secondary: 'bg-white text-slate-900 border border-slate-200 hover:bg-slate-50 focus:ring-slate-300',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-300'
  }

  return (
    <Component
      className={`inline-flex items-center justify-center rounded-xl px-4 py-2.5 text-sm font-semibold transition focus:outline-none focus:ring-4 disabled:cursor-not-allowed disabled:opacity-60 ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </Component>
  )
}
