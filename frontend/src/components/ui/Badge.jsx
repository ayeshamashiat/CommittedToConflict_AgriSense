import clsx from 'clsx'

const VARIANT_CLASSES = {
  success: 'bg-leaf-100 text-leaf-700 border-leaf-200',
  warning: 'bg-amber-100 text-amber-800 border-amber-200',
  danger: 'bg-red-100 text-red-700 border-red-200',
  info: 'bg-sky-100 text-sky-700 border-sky-200',
  neutral: 'bg-stone-100 text-stone-600 border-stone-200',
}

export default function Badge({ children, variant = 'neutral', className }) {
  return (
    <span
      className={clsx(
        'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium',
        VARIANT_CLASSES[variant] ?? VARIANT_CLASSES.neutral,
        className,
      )}
    >
      {children}
    </span>
  )
}
