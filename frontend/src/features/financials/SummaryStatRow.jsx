import Card from '../../components/ui/Card.jsx'
import { formatCurrencyBDT, formatPercent } from '../../lib/formatters.js'

export default function SummaryStatRow({ financials }) {
  const stats = [
    { label: 'Total Cost', value: formatCurrencyBDT(financials.totalCostBDT) },
    { label: 'Expected Revenue', value: formatCurrencyBDT(financials.expectedRevenueBDT) },
    { label: 'Net Profit', value: formatCurrencyBDT(financials.netProfitBDT), emphasis: true },
    { label: 'ROI', value: formatPercent(financials.roiPercent) },
    { label: 'Break-even', value: financials.breakEvenUnits },
  ]

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
      {stats.map((stat) => (
        <Card key={stat.label} className={stat.emphasis ? 'bg-leaf-50' : undefined}>
          <p className="text-xs text-stone-500">{stat.label}</p>
          <p className={`mt-1 text-lg font-semibold ${stat.emphasis ? 'text-leaf-700' : 'text-stone-800'}`}>
            {stat.value}
          </p>
        </Card>
      ))}
    </div>
  )
}
