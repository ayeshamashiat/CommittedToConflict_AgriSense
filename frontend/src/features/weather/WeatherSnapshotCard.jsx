import Card from '../../components/ui/Card.jsx'

const CONDITION_ICON = {
  Sunny: '☀️',
  Cloudy: '☁️',
  'Partly Cloudy': '⛅',
  Rain: '🌧️',
}

export default function WeatherSnapshotCard({ weather }) {
  const { location, current } = weather

  return (
    <Card className="flex items-center gap-4">
      <span className="text-4xl">{CONDITION_ICON[current.condition] ?? '🌤️'}</span>
      <div className="flex-1">
        <p className="text-xs text-stone-500">{location}</p>
        <p className="text-2xl font-semibold text-stone-800">{current.tempC}°C</p>
        <p className="text-sm text-stone-600">{current.condition}</p>
      </div>
      <div className="flex flex-col gap-1 text-right text-xs text-stone-500">
        <span>Humidity: {current.humidityPercent}%</span>
        <span>Rain (24h): {current.rainfallMm24h}mm</span>
      </div>
    </Card>
  )
}
