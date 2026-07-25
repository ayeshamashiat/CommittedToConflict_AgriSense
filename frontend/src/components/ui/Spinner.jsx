import clsx from 'clsx'

export default function Spinner({ className }) {
  return (
    <span
      role="status"
      aria-label="Loading"
      className={clsx(
        'inline-block h-4 w-4 animate-spin rounded-full border-2 border-leaf-200 border-t-leaf-600',
        className,
      )}
    />
  )
}
