import { useState } from 'react'
import Card from '../../components/ui/Card.jsx'
import Badge from '../../components/ui/Badge.jsx'
import Button from '../../components/ui/Button.jsx'
import EmptyState from '../../components/ui/EmptyState.jsx'
import FormField from '../profile/FormField.jsx'
import { useAppState } from '../../context/useAppState.js'
import { useTranslation } from '../../context/useTranslation.js'
import { fetchPriceIntelligence } from '../../api/client.js'
import { FORM_INPUT_CLASS } from '../../lib/constants.js'
import { formatCurrencyBDT } from '../../lib/formatters.js'

const RECOMMENDATION_COPY = {
  sell_now: { label: 'Sell Now', variant: 'warning' },
  store_and_wait: { label: 'Store & Wait', variant: 'success' },
}

export default function PriceIntelligencePage() {
  const { state } = useAppState()
  const { t } = useTranslation()
  const defaultCrop = state.recommendations[0]?.cropName ?? ''

  const [crop, setCrop] = useState(defaultCrop)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  const lookUp = async () => {
    if (!crop.trim()) return
    setError(null)
    setLoading(true)
    try {
      const data = await fetchPriceIntelligence(crop.trim(), state.currentSessionId)
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const maxPrice = result ? Math.max(...result.historicalPrices.map((p) => p.price)) : 1

  return (
    <div className="flex h-full flex-col overflow-y-auto">
      <h1 className="px-4 pt-4 text-2xl font-semibold text-leaf-800 sm:px-6 sm:pt-6">{t('nav_prices')}</h1>
      <div className="flex flex-col gap-4 p-4">
        <Card className="flex flex-col gap-4">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <FormField label="Crop">
              <input
                type="text"
                value={crop}
                onChange={(e) => setCrop(e.target.value)}
                placeholder="e.g. rice, tomato"
                className={FORM_INPUT_CLASS}
              />
            </FormField>
            <div className="flex items-end">
              <Button variant="primary" onClick={lookUp} disabled={loading || !crop.trim()}>
                {loading ? 'Checking…' : 'Check Price'}
              </Button>
            </div>
          </div>
          {error && <p className="text-xs text-red-600">{error}</p>}
        </Card>

        {result ? (
          <>
            <Card className="flex flex-col gap-3">
              <div className="flex flex-wrap items-center gap-2">
                <h4 className="text-sm font-semibold text-stone-700">
                  {result.crop.replace(/_/g, ' ')} — current price
                </h4>
                <Badge variant={RECOMMENDATION_COPY[result.recommendation]?.variant ?? 'neutral'}>
                  {RECOMMENDATION_COPY[result.recommendation]?.label ?? result.recommendation}
                </Badge>
              </div>
              <p className="text-2xl font-semibold text-leaf-700">
                {formatCurrencyBDT(result.currentPrice)}
                <span className="ml-1 text-sm font-normal text-stone-400">/{result.unit}</span>
              </p>
              <p className="text-sm text-stone-600">{result.reasoning}</p>
              <p className="text-xs text-stone-400">Source: {result.priceSource}</p>
              <p className="text-xs text-stone-400">{result.confidence}</p>
            </Card>

            <Card className="flex flex-col gap-3">
              <h4 className="text-sm font-semibold text-stone-700">Seasonal Price Trend (illustrative)</h4>
              <div className="flex items-end gap-2 pt-2" style={{ height: '120px' }}>
                {result.historicalPrices.map((p) => (
                  <div key={p.monthsAgo} className="flex flex-1 flex-col items-center gap-1">
                    <div
                      className="w-full rounded-t bg-leaf-400"
                      style={{ height: `${Math.max(6, (p.price / maxPrice) * 100)}px` }}
                      title={formatCurrencyBDT(p.price)}
                    />
                    <span className="text-[10px] text-stone-400">
                      {p.monthsAgo === 0 ? 'Now' : `-${p.monthsAgo}mo`}
                    </span>
                  </div>
                ))}
              </div>
            </Card>
          </>
        ) : (
          <EmptyState
            icon="📈"
            title="No price check yet"
            description="Enter a crop above to see its current price and a sell-now vs. store-and-wait recommendation."
          />
        )}
      </div>
    </div>
  )
}
