import { useState } from 'react'
import Card from '../../components/ui/Card.jsx'
import Button from '../../components/ui/Button.jsx'
import FormField from './FormField.jsx'
import { useAppState } from '../../context/useAppState.js'
import { FORM_INPUT_CLASS } from '../../lib/constants.js'

export default function PersonalDetailsForm() {
  const { state, dispatch } = useAppState()
  const [form, setForm] = useState(state.farmerProfile)

  const updateField = (field) => (e) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }))
  }

  const handleSave = () => {
    dispatch({ type: 'SET_PROFILE', payload: form })
  }

  return (
    <Card className="flex flex-col gap-4">
      <FormField label="Farmer Name">
        <input
          type="text"
          value={form.farmerName}
          onChange={updateField('farmerName')}
          placeholder="e.g. Abdul Karim"
          className={FORM_INPUT_CLASS}
        />
      </FormField>
      <FormField label="Phone Number">
        <input
          type="tel"
          value={form.phoneNumber}
          onChange={updateField('phoneNumber')}
          placeholder="e.g. +880 1XXX-XXXXXX"
          className={FORM_INPUT_CLASS}
        />
      </FormField>
      <div className="flex justify-end">
        <Button variant="primary" onClick={handleSave}>
          Save
        </Button>
      </div>
    </Card>
  )
}
