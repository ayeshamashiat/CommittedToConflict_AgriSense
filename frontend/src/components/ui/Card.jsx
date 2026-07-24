import clsx from 'clsx'

export default function Card({ children, className, padding = true }) {
  return (
    <div
      className={clsx(
        'rounded-xl border border-earth-100 bg-wheat-50 shadow-sm',
        padding && 'p-4',
        className,
      )}
    >
      {children}
    </div>
  )
}
