import Card from '../../components/ui/Card.jsx'
import { formatCurrencyBDT } from '../../lib/formatters.js'

export default function IrrigationScheduleList({ schedule }) {
  if (!schedule || schedule.events.length === 0) return null

  return (
    <Card className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h4 className="text-base font-semibold text-stone-800">Irrigation Schedule</h4>
        <span className="rounded-full bg-sky-100 px-3 py-1 text-sm font-bold text-sky-800">
          Total {formatCurrencyBDT(schedule.totalCostBDT)}
        </span>
      </div>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        {schedule.events.map((e, i) => (
          <div
            key={`${e.stage}_${i}`}
            className="flex items-start justify-between gap-3 rounded-lg border border-earth-100 bg-wheat-100/40 p-3"
          >
            <div>
              <p className="text-sm font-bold text-stone-800">{e.stage}</p>
              <p className="text-xs text-stone-500">
                Day {e.daysAfterSowing} — {e.note}
              </p>
            </div>
            <span className="shrink-0 text-sm font-bold text-sky-700">{formatCurrencyBDT(e.costBDT)}</span>
          </div>
        ))}
      </div>
      {schedule.notes && <p className="text-xs text-stone-400">{schedule.notes}</p>}
    </Card>
  )
}
