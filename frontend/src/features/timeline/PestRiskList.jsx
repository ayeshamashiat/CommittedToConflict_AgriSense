import clsx from 'clsx'
import Card from '../../components/ui/Card.jsx'
import Badge from '../../components/ui/Badge.jsx'
import { RISK_BADGE_VARIANT } from '../../lib/constants.js'
import { formatCurrencyBDT } from '../../lib/formatters.js'

// Left-accent + background tint per risk level — lets a farmer scanning the
// page tell high-risk items apart from low-risk ones at a glance, before
// reading any text.
const RISK_CARD_ACCENT = {
  High: 'border-l-red-400 bg-red-50/60',
  Medium: 'border-l-amber-400 bg-amber-50/50',
  Low: 'border-l-leaf-400 bg-leaf-50/40',
}

function groupByStage(risks) {
  const groups = []
  let current = null
  for (const r of risks) {
    if (!current || current.stage !== r.growthStage) {
      current = { stage: r.growthStage, daysAfterSowing: r.daysAfterSowing, items: [] }
      groups.push(current)
    }
    current.items.push(r)
  }
  return groups
}

export default function PestRiskList({ pestRisks }) {
  if (!pestRisks || pestRisks.risks.length === 0) return null

  const totalCostBDT = pestRisks.risks.reduce((sum, r) => sum + (r.costBDT || 0), 0)
  const highRiskCount = pestRisks.risks.filter((r) => r.riskLevel === 'High').length
  const groups = groupByStage(pestRisks.risks)

  return (
    <Card className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h4 className="text-base font-semibold text-stone-800">Pest &amp; Disease Risk</h4>
        <div className="flex items-center gap-3 text-xs">
          {highRiskCount > 0 && (
            <span className="font-medium text-red-600">
              {highRiskCount} high-risk item{highRiskCount === 1 ? '' : 's'}
            </span>
          )}
          {totalCostBDT > 0 && (
            <span className="rounded-full bg-stone-100 px-2.5 py-1 font-semibold text-stone-700">
              Est. total {formatCurrencyBDT(totalCostBDT)}
            </span>
          )}
        </div>
      </div>
      {pestRisks.source && <p className="-mt-2 text-xs text-stone-400">{pestRisks.source}</p>}

      <div className="flex flex-col gap-5">
        {groups.map((group) => (
          <div key={group.stage ?? 'unstaged'}>
            {group.stage && (
              <p className="mb-2 text-xs font-bold uppercase tracking-wide text-leaf-700">
                {group.stage}
                {group.daysAfterSowing != null && (
                  <span className="ml-1.5 font-normal normal-case text-stone-400">
                    (~day {group.daysAfterSowing} after sowing)
                  </span>
                )}
              </p>
            )}
            <div className="grid grid-cols-1 gap-3 md:grid-cols-2 2xl:grid-cols-3">
              {group.items.map((r, i) => (
                <div
                  key={`${r.name}_${i}`}
                  className={clsx(
                    'rounded-lg border border-earth-100 border-l-4 p-3 shadow-sm',
                    RISK_CARD_ACCENT[r.riskLevel] ?? 'border-l-stone-300',
                  )}
                >
                  <div className="flex flex-wrap items-start justify-between gap-2">
                    <p className="text-sm font-bold text-stone-800">{r.name}</p>
                    <Badge variant={RISK_BADGE_VARIANT[r.riskLevel] ?? 'neutral'}>{r.riskLevel} risk</Badge>
                  </div>
                  <div className="mt-1 flex flex-wrap items-center gap-2">
                    <Badge variant="neutral">{r.kind}</Badge>
                    {r.costBDT > 0 && (
                      <span className="text-xs font-semibold text-stone-600">
                        Est. treatment {formatCurrencyBDT(r.costBDT)}
                      </span>
                    )}
                  </div>
                  <p className="mt-2 text-xs text-stone-500">{r.triggerReason}</p>
                  <div className="mt-2 flex flex-col gap-1.5 text-xs text-stone-600">
                    <p>
                      <span className="font-semibold text-stone-700">Prevention: </span>
                      {r.prevention}
                    </p>
                    <p>
                      <span className="font-semibold text-stone-700">Treatment: </span>
                      {r.treatment}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </Card>
  )
}
