import { useState } from 'react'
import Card from '../../components/ui/Card.jsx'
import Button from '../../components/ui/Button.jsx'
import Badge from '../../components/ui/Badge.jsx'
import EmptyState from '../../components/ui/EmptyState.jsx'
import FormField from './FormField.jsx'
import { useAppState } from '../../context/useAppState.js'
import { FORM_INPUT_CLASS, LEVEL_BADGE_VARIANT } from '../../lib/constants.js'
import { formatCurrencyBDT } from '../../lib/formatters.js'

const SEASONS = ['Rabi', 'Kharif', 'Summer']

export default function CurrentCropSection() {
  const { state, dispatch } = useAppState()
  const [form, setForm] = useState(state.farmerProfile)
  const topCrop = state.recommendations[0]

  const updateField = (field, isNumeric = false) => (e) => {
    const rawValue = e.target.value
    const value = isNumeric ? (rawValue === '' ? null : Number(rawValue)) : rawValue
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  const handleSave = () => {
    dispatch({ type: 'SET_PROFILE', payload: form })
  }

  return (
    <div className="flex flex-col gap-4">
      <Card className="flex flex-col gap-4">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <FormField label="Season">
            <select value={form.season} onChange={updateField('season')} className={FORM_INPUT_CLASS}>
              <option value="">Select…</option>
              {SEASONS.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </FormField>
          <FormField label="Budget (BDT)">
            <input
              type="number"
              min="0"
              step="500"
              value={form.budgetBDT ?? ''}
              onChange={updateField('budgetBDT', true)}
              className={FORM_INPUT_CLASS}
            />
          </FormField>
        </div>
        <div className="flex justify-end">
          <Button variant="primary" onClick={handleSave}>
            Save
          </Button>
        </div>
      </Card>

      <Card>
        <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-leaf-700">Agent's Top Pick</h3>
        {topCrop ? (
          <div className="flex flex-col gap-2">
            <div className="flex items-center justify-between">
              <span className="text-base font-semibold text-stone-800">{topCrop.cropName}</span>
              <Badge variant={LEVEL_BADGE_VARIANT[topCrop.suitability] ?? 'neutral'}>
                {topCrop.suitability} suitability
              </Badge>
            </div>
            <p className="text-sm text-stone-600">{topCrop.reasoning}</p>
            <p className="text-sm font-medium text-leaf-700">
              Estimated Profit: {formatCurrencyBDT(topCrop.estimatedProfitBDT)}
            </p>
          </div>
        ) : (
          <EmptyState
            icon="🌱"
            title="No crop selected yet"
            description="Chat with the AI Assistant to get ranked crop options for your farm."
          />
        )}
      </Card>
    </div>
  )
}
