import clsx from 'clsx'
import Card from '../../components/ui/Card.jsx'
import { formatCurrencyBDT } from '../../lib/formatters.js'

export default function FertilizerScheduleTable({ schedule }) {
  if (!schedule || schedule.stages.length === 0) return null

  return (
    <Card className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h4 className="text-base font-semibold text-stone-800">Fertilizer Schedule</h4>
        <span className="rounded-full bg-leaf-100 px-3 py-1 text-sm font-bold text-leaf-800">
          Total {formatCurrencyBDT(schedule.totalCostBDT)}
        </span>
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        {schedule.stages.map((s, i) => (
          <div key={`${s.stage}_${i}`} className="rounded-lg border border-earth-100 bg-wheat-100/40 p-3">
            <p className="text-xs font-bold uppercase tracking-wide text-leaf-700">{s.stage}</p>
            <p className="text-xs text-stone-400">Day {s.daysAfterSowing}</p>
            <p className="mt-2 text-lg font-bold text-stone-800">{formatCurrencyBDT(s.costBDT)}</p>
          </div>
        ))}
      </div>

      <div className="overflow-x-auto rounded-lg border border-earth-100">
        <table className="w-full min-w-[560px] text-sm">
          <thead>
            <tr className="border-b border-earth-100 bg-wheat-100/60 text-left text-stone-500">
              <th className="py-2.5 pl-3 pr-2 font-semibold">Stage</th>
              <th className="py-2.5 pr-2 font-semibold">Day</th>
              <th className="py-2.5 pr-2 text-right font-semibold">Urea (kg)</th>
              <th className="py-2.5 pr-2 text-right font-semibold">TSP (kg)</th>
              <th className="py-2.5 pr-2 text-right font-semibold">MoP (kg)</th>
              <th className="py-2.5 pr-2 text-right font-semibold">Cost</th>
              <th className="py-2.5 pr-3 font-semibold">Organic alternative</th>
            </tr>
          </thead>
          <tbody>
            {schedule.stages.map((s, i) => (
              <tr
                key={`${s.stage}_${i}`}
                className={clsx('border-b border-earth-100/60 align-top last:border-0', i % 2 === 1 && 'bg-wheat-100/30')}
              >
                <td className="py-2.5 pl-3 pr-2 font-semibold text-stone-800">{s.stage}</td>
                <td className="py-2.5 pr-2 text-stone-500">Day {s.daysAfterSowing}</td>
                <td className="py-2.5 pr-2 text-right text-stone-700">{s.ureaKg}</td>
                <td className="py-2.5 pr-2 text-right text-stone-700">{s.tspKg}</td>
                <td className="py-2.5 pr-2 text-right text-stone-700">{s.mopKg}</td>
                <td className="py-2.5 pr-2 text-right font-bold text-leaf-700">{formatCurrencyBDT(s.costBDT)}</td>
                <td className="py-2.5 pr-3 text-stone-500">{s.organicAlternative || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {schedule.notes && <p className="text-xs text-stone-400">{schedule.notes}</p>}
    </Card>
  )
}
