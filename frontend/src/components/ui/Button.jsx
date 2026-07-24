import clsx from 'clsx'

const VARIANT_CLASSES = {
  primary: 'bg-leaf-600 text-wheat-50 hover:bg-leaf-700 disabled:bg-leaf-300',
  secondary: 'bg-earth-100 text-earth-700 hover:bg-earth-100/70 disabled:opacity-50',
  ghost: 'bg-transparent text-leaf-700 hover:bg-leaf-50 disabled:opacity-50',
}

const SIZE_CLASSES = {
  sm: 'px-2.5 py-1 text-xs',
  md: 'px-4 py-2 text-sm',
}

export default function Button({
  children,
  variant = 'primary',
  size = 'md',
  className,
  type = 'button',
  ...props
}) {
  return (
    <button
      type={type}
      className={clsx(
        'inline-flex items-center justify-center gap-1.5 rounded-lg font-medium transition-colors disabled:cursor-not-allowed',
        VARIANT_CLASSES[variant],
        SIZE_CLASSES[size],
        className,
      )}
      {...props}
    >
      {children}
    </button>
  )
}
