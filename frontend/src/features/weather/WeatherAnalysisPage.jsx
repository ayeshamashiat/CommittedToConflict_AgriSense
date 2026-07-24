import Card from '../../components/ui/Card.jsx'
import EmptyState from '../../components/ui/EmptyState.jsx'
import WeatherSnapshotCard from './WeatherSnapshotCard.jsx'
import WeatherForecastList from './WeatherForecastList.jsx'
import { useAppState } from '../../context/useAppState.js'

export default function WeatherAnalysisPage() {
  const { state } = useAppState()
  const { weather, alerts } = state

  if (!weather) {
    return (
      <div className="p-4 sm:p-6">
        <h1 className="mb-4 text-2xl font-semibold text-leaf-800">Weather Analysis</h1>
        <EmptyState
          icon="☁️"
          title="No weather data yet"
          description="Chat with the AI Assistant to fetch a forecast for your farm's location."
        />
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-4 p-4 sm:p-6">
      <h1 className="text-2xl font-semibold text-leaf-800">Weather Analysis</h1>

      <WeatherSnapshotCard weather={weather} />

      <div>
        <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-leaf-700">7-Day Forecast</h2>
        <WeatherForecastList forecast={weather.forecast} />
      </div>

      <Card>
        <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-leaf-700">Impact on Your Plan</h2>
        {alerts.length === 0 ? (
          <p className="text-sm text-stone-500">No plan adjustments triggered by the current forecast.</p>
        ) : (
          <ul className="flex flex-col gap-2">
            {alerts.map((alert) => (
              <li key={alert.id} className="text-sm text-stone-600">
                <span className="font-medium text-stone-800">{alert.relatedStage ?? 'Plan'}:</span> {alert.message}{' '}
                <span className="text-stone-400">— {alert.reasoning}</span>
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  )
}
