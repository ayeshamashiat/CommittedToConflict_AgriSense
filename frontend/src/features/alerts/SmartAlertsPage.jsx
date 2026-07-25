import AlertCard from './AlertCard.jsx'
import EmptyState from '../../components/ui/EmptyState.jsx'
import { useAppState } from '../../context/useAppState.js'

export default function SmartAlertsPage() {
  const { state, dispatch } = useAppState()
  const { alerts } = state

  return (
    <div className="flex h-full flex-col overflow-y-auto p-4 sm:p-6">
      <h1 className="mb-4 text-2xl font-semibold text-leaf-800">Smart Alerts</h1>
      {alerts.length === 0 ? (
        <EmptyState
          icon="🔔"
          title="No alerts right now"
          description="Weather-triggered advice will appear here once your season plan is generated."
        />
      ) : (
        <div className="flex flex-col gap-3">
          {alerts.map((alert) => (
            <AlertCard
              key={alert.id}
              alert={alert}
              onDismiss={(id) => dispatch({ type: 'DISMISS_ALERT', payload: id })}
            />
          ))}
        </div>
      )}
    </div>
  )
}
