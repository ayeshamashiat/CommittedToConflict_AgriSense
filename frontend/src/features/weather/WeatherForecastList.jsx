import { formatDate } from '../../lib/formatters.js'

const CONDITION_ICON = {
  Sunny: '☀️',
  Cloudy: '☁️',
  'Partly Cloudy': '⛅',
  Rain: '🌧️',
}

export default function WeatherForecastList({ forecast }) {
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-7">
      {forecast.map((day) => (
        <div key={day.date} className="flex flex-col items-center gap-1 rounded-lg border border-earth-100 bg-wheat-50 p-3 text-center">
          <span className="text-xs font-medium text-stone-500">{day.day}</span>
          <span className="text-[10px] text-stone-400">{formatDate(day.date)}</span>
          <span className="text-2xl">{CONDITION_ICON[day.condition] ?? '🌤️'}</span>
          <span className="text-sm font-semibold text-stone-800">{day.tempC}°C</span>
          <span className="text-xs text-sky-600">{day.rainfallMm}mm</span>
        </div>
      ))}
    </div>
  )
}
