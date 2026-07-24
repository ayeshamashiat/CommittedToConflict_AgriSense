import clsx from 'clsx'
import { useAppState } from '../context/useAppState.js'
import { NAV_SECTIONS } from '../lib/constants.js'

export default function Sidebar() {
  const { state, dispatch } = useAppState()
  const { activeSection, isSidebarOpen } = state.ui

  const goToSection = (id) => dispatch({ type: 'SET_SECTION', payload: id })

  return (
    <>
      {isSidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/30 lg:hidden"
          onClick={() => dispatch({ type: 'TOGGLE_SIDEBAR' })}
          aria-hidden="true"
        />
      )}

      <nav
        className={clsx(
          'fixed inset-y-0 left-0 z-40 flex w-64 shrink-0 flex-col gap-1 overflow-y-auto border-r border-earth-100 bg-leaf-800 p-3 text-wheat-50 shadow-lg transition-transform duration-200',
          'lg:static lg:z-auto lg:translate-x-0 lg:shadow-none',
          isSidebarOpen ? 'translate-x-0' : '-translate-x-full',
        )}
      >
        <div className="mb-3 flex items-center gap-2 px-2 py-1">
          <span className="text-xl">🌾</span>
          <span className="font-semibold tracking-tight">AgriSense AI</span>
        </div>

        {NAV_SECTIONS.map((section) => {
          const isActive = section.id === activeSection
          const alertCount = section.id === 'alerts' ? state.alerts.length : 0

          return (
            <button
              key={section.id}
              type="button"
              onClick={() => goToSection(section.id)}
              className={clsx(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-left text-sm font-medium transition-colors',
                isActive ? 'bg-leaf-600 text-wheat-50' : 'text-leaf-100 hover:bg-leaf-700',
              )}
            >
              <span className="text-base">{section.icon}</span>
              <span className="flex-1">{section.label}</span>
              {alertCount > 0 && (
                <span className="flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-[10px] font-semibold text-white">
                  {alertCount}
                </span>
              )}
            </button>
          )
        })}
      </nav>
    </>
  )
}
