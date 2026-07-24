import EmptyState from '../../components/ui/EmptyState.jsx'
import WeatherSnapshotCard from '../weather/WeatherSnapshotCard.jsx'
import { useAppState } from '../../context/useAppState.js'

export default function LiveWeatherWidget() {
  const { state } = useAppState()
  const { weather } = state

  if (!weather) {
    return (
      <EmptyState
        icon="☁️"
        title="No weather data yet"
        description="Chat with the AI Assistant to fetch live conditions for your farm's location."
      />
    )
  }

  return <WeatherSnapshotCard weather={weather} />
}
