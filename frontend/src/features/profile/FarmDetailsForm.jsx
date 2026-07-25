import { useState } from 'react'
import Card from '../../components/ui/Card.jsx'
import Button from '../../components/ui/Button.jsx'
import FormField from './FormField.jsx'
import { useAppState } from '../../context/useAppState.js'
import { FORM_INPUT_CLASS } from '../../lib/constants.js'

const SOIL_TYPES = ['Sandy', 'Loamy', 'Clay', 'Silty', 'Peaty']
const WATER_LEVELS = ['Low', 'Medium', 'High']

export default function FarmDetailsForm() {
  const { state, dispatch } = useAppState()
  const [form, setForm] = useState(state.farmerProfile)

  const updateField = (field, isNumeric = false) => (e) => {
    const rawValue = e.target.value
    const value = isNumeric ? (rawValue === '' ? null : Number(rawValue)) : rawValue
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  const handleSave = () => {
    dispatch({ type: 'SET_PROFILE', payload: form })
  }

  return (
    <Card className="flex flex-col gap-4">
      <FormField label="Location">
        <input
          type="text"
          value={form.location}
          onChange={updateField('location')}
          placeholder="e.g. Rangpur, Bangladesh"
          className={FORM_INPUT_CLASS}
        />
      </FormField>
      <FormField label="Farm Size (acres)">
        <input
          type="number"
          min="0"
          step="0.1"
          value={form.farmSizeAcres ?? ''}
          onChange={updateField('farmSizeAcres', true)}
          className={FORM_INPUT_CLASS}
        />
      </FormField>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <FormField label="Soil Type">
          <select value={form.soilType} onChange={updateField('soilType')} className={FORM_INPUT_CLASS}>
            <option value="">Select…</option>
            {SOIL_TYPES.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </FormField>
        <FormField label="Water Availability">
          <select value={form.waterAvailability} onChange={updateField('waterAvailability')} className={FORM_INPUT_CLASS}>
            <option value="">Select…</option>
            {WATER_LEVELS.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </FormField>
      </div>
      <div className="flex justify-end">
        <Button variant="primary" onClick={handleSave}>
          Save
        </Button>
      </div>
    </Card>
  )
}
