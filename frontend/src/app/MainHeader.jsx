import Badge from '../components/ui/Badge.jsx'
import { useAppState } from '../context/useAppState.js'
import { NAV_SECTIONS } from '../lib/constants.js'

const USE_MOCK = import.meta.env.VITE_USE_MOCK !== 'false'

export default function MainHeader() {
  const { state, dispatch } = useAppState()
  const activeSection = NAV_SECTIONS.find((section) => section.id === state.ui.activeSection)

  return (
    <header className="flex h-14 shrink-0 items-center gap-3 border-b border-earth-100 bg-wheat-50 px-3 sm:px-4">
      <button
        type="button"
        onClick={() => dispatch({ type: 'TOGGLE_SIDEBAR' })}
        className="rounded-lg p-2 text-stone-600 hover:bg-wheat-200 lg:hidden"
        aria-label="Toggle navigation"
      >
        <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>

      <h1 className="flex-1 truncate text-base font-semibold text-stone-800">
        {activeSection ? `${activeSection.icon} ${activeSection.label}` : ''}
      </h1>

      {USE_MOCK && <Badge variant="warning">Mock Data Mode</Badge>}
    </header>
  )
}
