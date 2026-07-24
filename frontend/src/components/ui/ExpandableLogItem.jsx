import { useState } from 'react'
import clsx from 'clsx'

export default function ExpandableLogItem({ summary, defaultOpen = false, children }) {
  const [isOpen, setIsOpen] = useState(defaultOpen)

  return (
    <div className="rounded-lg border border-earth-100 bg-wheat-50">
      <button
        type="button"
        onClick={() => setIsOpen((open) => !open)}
        className="flex w-full items-center justify-between gap-2 px-3 py-2 text-left"
      >
        {summary}
        <svg
          className={clsx('h-4 w-4 shrink-0 text-stone-400 transition-transform', isOpen && 'rotate-180')}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      {isOpen && <div className="border-t border-earth-100 px-3 py-2">{children}</div>}
    </div>
  )
}
