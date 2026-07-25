import { useEffect, useState } from 'react'
import Card from '../../components/ui/Card.jsx'
import Button from '../../components/ui/Button.jsx'
import EmptyState from '../../components/ui/EmptyState.jsx'
import FormField from '../profile/FormField.jsx'
import SupplierOffersTable from './SupplierOffersTable.jsx'
import { useAppState } from '../../context/useAppState.js'
import { useTranslation } from '../../context/useTranslation.js'
import { fetchMarketplace } from '../../api/client.js'
import { FORM_INPUT_CLASS } from '../../lib/constants.js'

const ITEMS = [
  { value: 'urea', label: 'Urea' },
  { value: 'tsp', label: 'TSP' },
  { value: 'mop', label: 'MoP' },
  { value: 'pesticide', label: 'Pesticide' },
  { value: 'seed', label: 'Seed' },
]

export default function MarketplacePage() {
  const { state } = useAppState()
  const { t } = useTranslation()
  const defaultCrop = state.recommendations[0]?.cropName ?? ''

  const [item, setItem] = useState('urea')
  const [crop, setCrop] = useState(defaultCrop)
  const [quantity, setQuantity] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [offers, setOffers] = useState(state.marketplaceOffers)

  // A chat lookup ("where can I buy urea") may have already populated this —
  // reflect it here so the two surfaces (chat + page) show the same data.
  useEffect(() => {
    if (state.marketplaceOffers) setOffers(state.marketplaceOffers)
  }, [state.marketplaceOffers])

  const compare = async () => {
    setError(null)
    setLoading(true)
    try {
      const result = await fetchMarketplace({
        item,
        crop: item === 'seed' ? crop || defaultCrop : undefined,
        quantity: quantity ? Number(quantity) : undefined,
        location: state.farmerProfile.location,
      })
      setOffers(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex h-full flex-col overflow-y-auto">
      <h1 className="px-4 pt-4 text-2xl font-semibold text-leaf-800 sm:px-6 sm:pt-6">{t('nav_marketplace')}</h1>
      <div className="flex flex-col gap-4 p-4">
        <Card className="flex flex-col gap-4">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
            <FormField label="Input needed">
              <select value={item} onChange={(e) => setItem(e.target.value)} className={FORM_INPUT_CLASS}>
                {ITEMS.map((o) => (
                  <option key={o.value} value={o.value}>
                    {o.label}
                  </option>
                ))}
              </select>
            </FormField>
            {item === 'seed' && (
              <FormField label="Crop">
                <input
                  type="text"
                  value={crop}
                  onChange={(e) => setCrop(e.target.value)}
                  placeholder="e.g. rice, potato"
                  className={FORM_INPUT_CLASS}
                />
              </FormField>
            )}
            <FormField label="Quantity (optional)">
              <input
                type="number"
                min="0"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
                placeholder="e.g. 50"
                className={FORM_INPUT_CLASS}
              />
            </FormField>
            <div className="flex items-end">
              <Button variant="primary" onClick={compare} disabled={loading || (item === 'seed' && !crop)}>
                {loading ? 'Comparing…' : 'Compare Suppliers'}
              </Button>
            </div>
          </div>
          {error && <p className="text-xs text-red-600">{error}</p>}
        </Card>

        {offers ? (
          <SupplierOffersTable offers={offers} />
        ) : (
          <EmptyState
            icon="🛒"
            title="No comparison yet"
            description="Pick an input above and compare suppliers, or ask the AI Assistant 'where can I buy urea?'"
          />
        )}
      </div>
    </div>
  )
}
