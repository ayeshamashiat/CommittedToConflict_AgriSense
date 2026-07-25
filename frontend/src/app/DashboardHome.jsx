import Card from '../components/ui/Card.jsx'
import Badge from '../components/ui/Badge.jsx'
import Button from '../components/ui/Button.jsx'
import WeatherSnapshotCard from '../features/weather/WeatherSnapshotCard.jsx'
import { useAppState } from '../context/useAppState.js'
import { useTranslation } from '../context/useTranslation.js'
import { LEVEL_BADGE_VARIANT } from '../lib/constants.js'
import { formatCurrencyBDT, formatPercent } from '../lib/formatters.js'

function DashboardCard({ title, onClick, children }) {
  return (
    <Card
      className="flex cursor-pointer flex-col gap-2 transition-shadow hover:shadow-md"
      padding={false}
    >
      <button type="button" onClick={onClick} className="flex flex-col gap-2 p-4 text-left">
        <p className="text-xs font-semibold uppercase tracking-wide text-leaf-700">{title}</p>
        {children}
      </button>
    </Card>
  )
}

export default function DashboardHome() {
  const { state, dispatch } = useAppState()
  const { t } = useTranslation()
  const { farmerProfile, recommendations, financials, alerts, weather } = state
  const goTo = (section) => dispatch({ type: 'SET_SECTION', payload: section })

  if (recommendations.length === 0) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-4 p-6 text-center">
        <span className="text-4xl">🌾</span>
        <h1 className="text-2xl font-semibold text-leaf-800">Welcome to AgriSense AI</h1>
        <p className="max-w-md text-sm text-stone-500">
          Chat with the AI Assistant about your farm to get a costed, weather-aware season plan. Once it's ready,
          this dashboard will summarize everything in one place.
        </p>
        <Button variant="primary" onClick={() => goTo('assistant')}>
          Open AI Assistant →
        </Button>
      </div>
    )
  }

  const topCrop = recommendations[0]
  const latestAlert = alerts[0]

  return (
    <div className="flex flex-col gap-4 p-4 sm:p-6">
      <h1 className="text-2xl font-semibold text-leaf-800">{t('nav_dashboard')}</h1>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <DashboardCard title="Farmer Profile" onClick={() => goTo('profile')}>
          <p className="text-lg font-semibold text-stone-800">{farmerProfile.farmerName || 'Your Farm'}</p>
          <p className="text-sm text-stone-500">
            {farmerProfile.location} · {farmerProfile.farmSizeAcres ?? '—'} acres · {farmerProfile.season}
          </p>
        </DashboardCard>

        <DashboardCard title="Top Crop Pick" onClick={() => goTo('crops')}>
          <div className="flex items-center justify-between">
            <p className="text-lg font-semibold text-stone-800">{topCrop.cropName}</p>
            <Badge variant={LEVEL_BADGE_VARIANT[topCrop.suitability] ?? 'neutral'}>{topCrop.suitability}</Badge>
          </div>
          <p className="text-sm text-stone-500">Est. profit {formatCurrencyBDT(topCrop.estimatedProfitBDT)}</p>
        </DashboardCard>

        {financials && (
          <DashboardCard title="Financial Snapshot" onClick={() => goTo('financials')}>
            <p className="text-lg font-semibold text-leaf-700">{formatCurrencyBDT(financials.netProfitBDT)}</p>
            <p className="text-sm text-stone-500">Net profit · ROI {formatPercent(financials.roiPercent)}</p>
          </DashboardCard>
        )}

        {weather && (
          <button type="button" onClick={() => goTo('weather')} className="cursor-pointer text-left">
            <WeatherSnapshotCard weather={weather} />
          </button>
        )}

        {latestAlert && (
          <DashboardCard title="Latest Alert" onClick={() => goTo('alerts')}>
            <p className="text-sm font-semibold text-stone-800">{latestAlert.title}</p>
            <p className="text-sm text-stone-500">{latestAlert.message}</p>
          </DashboardCard>
        )}
      </div>
    </div>
  )
}
