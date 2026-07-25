import Card from '../../components/ui/Card.jsx'
import Badge from '../../components/ui/Badge.jsx'

const CONFIDENCE_COPY = {
  official: {
    variant: 'success',
    label: 'Official sources',
    blurb: 'Yield and price figures are both from cited government sources.',
  },
  mixed: {
    variant: 'warning',
    label: 'Mixed sources',
    blurb: 'Some cost components (e.g. seed, labor-days, or water) are estimated rather than sourced.',
  },
}

export default function DataSourcesCard({ financials }) {
  const confidence = CONFIDENCE_COPY[financials.dataConfidence] ?? CONFIDENCE_COPY.mixed

  return (
    <Card className="flex flex-col gap-3">
      <div className="flex flex-wrap items-center gap-2">
        <h4 className="text-sm font-semibold text-stone-700">Data Sources &amp; Confidence</h4>
        <Badge variant={confidence.variant}>{confidence.label}</Badge>
        {financials.withinBudget != null && (
          <Badge variant={financials.withinBudget ? 'success' : 'danger'}>
            {financials.withinBudget ? 'Within budget' : 'Over budget'}
          </Badge>
        )}
      </div>
      <p className="text-xs text-stone-500">{confidence.blurb}</p>
      {financials.yieldSource && (
        <p className="text-xs text-stone-600">
          <span className="font-medium text-stone-700">Yield source: </span>
          {financials.yieldSource}
        </p>
      )}
      {financials.priceSource && (
        <p className="text-xs text-stone-600">
          <span className="font-medium text-stone-700">Price source: </span>
          {financials.priceSource}
        </p>
      )}
      {financials.notes && (
        <p className="text-xs text-stone-500">
          <span className="font-medium text-stone-700">Note: </span>
          {financials.notes}
        </p>
      )}
    </Card>
  )
}
