import Card from '../../components/ui/Card.jsx'
import Badge from '../../components/ui/Badge.jsx'
import { LEVEL_BADGE_VARIANT, RISK_BADGE_VARIANT } from '../../lib/constants.js'
import { formatCurrencyBDT } from '../../lib/formatters.js'

export default function CropCard({ crop }) {
  return (
    <Card className="flex flex-col gap-3">
      <div className="flex items-start justify-between gap-2">
        <h3 className="text-base font-semibold text-leaf-800">{crop.cropName}</h3>
        <Badge variant={LEVEL_BADGE_VARIANT[crop.suitability] ?? 'neutral'}>
          {crop.suitability} suitability
        </Badge>
      </div>

      <div className="flex flex-wrap gap-2">
        <Badge variant={RISK_BADGE_VARIANT[crop.riskLevel] ?? 'neutral'}>Risk: {crop.riskLevel}</Badge>
        <Badge variant="info">Water: {crop.waterNeed}</Badge>
      </div>

      <div className="rounded-lg bg-leaf-50 px-3 py-2">
        <p className="text-xs text-stone-500">Estimated Profit</p>
        <p className="text-lg font-semibold text-leaf-700">{formatCurrencyBDT(crop.estimatedProfitBDT)}</p>
      </div>

      <p className="text-sm leading-relaxed text-stone-600">{crop.reasoning}</p>
    </Card>
  )
}
