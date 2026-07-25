import { useRef, useState } from 'react'
import Card from '../../components/ui/Card.jsx'
import Badge from '../../components/ui/Badge.jsx'
import Button from '../../components/ui/Button.jsx'
import FormField from '../profile/FormField.jsx'
import { useAppState } from '../../context/useAppState.js'
import { useTranslation } from '../../context/useTranslation.js'
import { detectDisease } from '../../api/client.js'
import { FORM_INPUT_CLASS, RISK_BADGE_VARIANT } from '../../lib/constants.js'
import { formatCurrencyBDT } from '../../lib/formatters.js'

const CONFIDENCE_VARIANT = { low: 'danger', medium: 'warning', high: 'success' }

export default function DiseaseDetectionPage() {
  const { state } = useAppState()
  const { t } = useTranslation()
  const fileInputRef = useRef(null)

  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [cropHint, setCropHint] = useState(state.recommendations[0]?.cropName ?? '')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  const onFileChange = (e) => {
    const selected = e.target.files?.[0]
    if (!selected) return
    setFile(selected)
    setResult(null)
    setError(null)
    setPreviewUrl(URL.createObjectURL(selected))
  }

  const analyze = async () => {
    if (!file) return
    setError(null)
    setLoading(true)
    try {
      const data = await detectDisease({ imageFile: file, cropHint, sessionId: state.currentSessionId })
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex h-full flex-col overflow-y-auto">
      <h1 className="px-4 pt-4 text-2xl font-semibold text-leaf-800 sm:px-6 sm:pt-6">{t('nav_disease')}</h1>
      <div className="flex flex-col gap-4 p-4">
        <Card className="flex flex-col gap-4">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <FormField label="Crop (optional)">
              <input
                type="text"
                value={cropHint}
                onChange={(e) => setCropHint(e.target.value)}
                placeholder="e.g. tomato"
                className={FORM_INPUT_CLASS}
              />
            </FormField>
            <FormField label="Leaf / plant photo">
              <input
                ref={fileInputRef}
                type="file"
                accept="image/jpeg,image/png,image/webp"
                capture="environment"
                onChange={onFileChange}
                className="block w-full text-sm text-stone-600 file:mr-3 file:rounded-lg file:border-0 file:bg-leaf-600 file:px-3 file:py-2 file:text-sm file:font-medium file:text-wheat-50 hover:file:bg-leaf-700"
              />
            </FormField>
            <div className="flex items-end">
              <Button variant="primary" onClick={analyze} disabled={loading || !file}>
                {loading ? 'Analyzing…' : 'Analyze Photo'}
              </Button>
            </div>
          </div>
          {previewUrl && (
            <img src={previewUrl} alt="Selected leaf/plant" className="max-h-64 rounded-lg border border-earth-100 object-contain" />
          )}
          {error && <p className="text-xs text-red-600">{error}</p>}
        </Card>

        {result && (
          <Card className="flex flex-col gap-3">
            <div className="flex flex-wrap items-center gap-2">
              <h4 className="text-sm font-semibold text-stone-700">
                {result.cropGuess} — {result.diseaseName}
              </h4>
              <Badge variant={CONFIDENCE_VARIANT[result.confidence] ?? 'neutral'}>
                {result.confidence} confidence
              </Badge>
              {result.isKnownInKnowledgeBase && <Badge variant="info">Matched to knowledge base</Badge>}
            </div>
            {result.symptomsObserved && <p className="text-sm text-stone-600">{result.symptomsObserved}</p>}
            {(result.prevention || result.treatment) && (
              <div className="grid grid-cols-1 gap-2 text-sm text-stone-600 sm:grid-cols-2">
                {result.prevention && (
                  <p>
                    <span className="font-medium text-stone-700">Prevention:</span> {result.prevention}
                  </p>
                )}
                {result.treatment && (
                  <p>
                    <span className="font-medium text-stone-700">Treatment:</span> {result.treatment}
                  </p>
                )}
              </div>
            )}
            {result.estimatedCostBDT != null && (
              <p className="text-sm text-stone-700">
                Est. treatment cost: <span className="font-semibold">{formatCurrencyBDT(result.estimatedCostBDT)}</span>
              </p>
            )}
            <p className="text-xs text-stone-400">{result.source}</p>
            <p className="rounded-lg bg-amber-50 p-2 text-xs text-amber-800">{result.disclaimer}</p>
          </Card>
        )}
      </div>
    </div>
  )
}
