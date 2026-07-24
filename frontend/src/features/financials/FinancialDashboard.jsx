import SummaryStatRow from './SummaryStatRow.jsx'
import CostBreakdownTable from './CostBreakdownTable.jsx'
import EmptyState from '../../components/ui/EmptyState.jsx'
import { useAppState } from '../../context/useAppState.js'
import { formatDate } from '../../lib/formatters.js'

export default function FinancialDashboard() {
  const { state } = useAppState()
  const { financials } = state

  if (!financials) {
    return (
      <EmptyState
        icon="💰"
        title="No financial projection yet"
        description="Costs, revenue, profit, and ROI will appear once a plan is generated."
      />
    )
  }

  return (
    <div className="flex flex-col gap-4 p-4">
      <SummaryStatRow financials={financials} />
      <div>
        <h4 className="mb-2 text-sm font-semibold text-stone-700">Itemized Costs</h4>
        <CostBreakdownTable costs={financials.costs} totalCostBDT={financials.totalCostBDT} />
      </div>
      {financials.breakEvenDate && (
        <p className="text-xs text-stone-400">Projected break-even date: {formatDate(financials.breakEvenDate)}</p>
      )}
    </div>
  )
}
