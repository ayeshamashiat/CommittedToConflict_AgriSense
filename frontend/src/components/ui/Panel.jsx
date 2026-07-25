import clsx from 'clsx'

export default function Panel({ title, action, children, className, contentClassName }) {
  return (
    <div className={clsx('flex h-full flex-col bg-wheat-50', className)}>
      <div className="flex shrink-0 items-center justify-between border-b border-earth-100 px-4 py-3">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-leaf-700">{title}</h2>
        {action}
      </div>
      <div className={clsx('flex-1 overflow-y-auto', contentClassName)}>{children}</div>
    </div>
  )
}
