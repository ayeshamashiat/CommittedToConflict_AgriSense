import { formatCurrencyBDT } from '../../lib/formatters.js'

export default function CostBreakdownTable({ costs, totalCostBDT }) {
  return (
    <table className="w-full max-w-md text-sm">
      <thead>
        <tr className="border-b border-earth-100 text-left text-stone-500">
          <th className="py-2 font-medium">Item</th>
          <th className="py-2 text-right font-medium">Cost</th>
        </tr>
      </thead>
      <tbody>
        {costs.map((item) => (
          <tr key={item.label} className="border-b border-earth-100/60">
            <td className="py-2 text-stone-700">{item.label}</td>
            <td className="py-2 text-right text-stone-800">{formatCurrencyBDT(item.amountBDT)}</td>
          </tr>
        ))}
      </tbody>
      <tfoot>
        <tr>
          <td className="pt-2 font-semibold text-stone-800">Total</td>
          <td className="pt-2 text-right font-semibold text-stone-800">{formatCurrencyBDT(totalCostBDT)}</td>
        </tr>
      </tfoot>
    </table>
  )
}
