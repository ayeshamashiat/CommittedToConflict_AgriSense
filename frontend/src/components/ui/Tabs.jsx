import clsx from 'clsx'

export default function Tabs({ tabs, activeId, onChange, className }) {
  return (
    <div className={clsx('flex gap-1 border-b border-earth-100', className)}>
      {tabs.map((tab) => {
        const isActive = tab.id === activeId
        return (
          <button
            key={tab.id}
            type="button"
            onClick={() => onChange(tab.id)}
            className={clsx(
              'border-b-2 px-4 py-2.5 text-sm font-medium transition-colors',
              isActive
                ? 'border-leaf-600 text-leaf-700'
                : 'border-transparent text-stone-500 hover:text-leaf-600',
            )}
          >
            {tab.label}
          </button>
        )
      })}
    </div>
  )
}
