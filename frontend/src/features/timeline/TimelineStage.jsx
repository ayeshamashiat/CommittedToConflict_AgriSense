import clsx from 'clsx'
import Badge from '../../components/ui/Badge.jsx'
import { TIMELINE_STAGE_VARIANT } from '../../lib/constants.js'
import { formatDateRange } from '../../lib/formatters.js'

export default function TimelineStage({ stage, isLast }) {
  return (
    <li className="relative flex gap-4 pb-6 last:pb-0">
      {!isLast && (
        <span className="absolute left-[7px] top-4 h-full w-0.5 bg-earth-100" aria-hidden="true" />
      )}
      <span
        className={clsx(
          'z-10 mt-1.5 h-4 w-4 shrink-0 rounded-full border-2 border-wheat-50',
          stage.status === 'completed' && 'bg-leaf-600',
          stage.status === 'current' && 'bg-sky-500',
          stage.status === 'upcoming' && 'bg-stone-300',
        )}
      />
      <div className="flex-1 pt-0.5">
        <div className="flex flex-wrap items-center gap-2">
          <h4 className="font-medium text-stone-800">{stage.name}</h4>
          <Badge variant={TIMELINE_STAGE_VARIANT[stage.status] ?? 'neutral'}>{stage.status}</Badge>
        </div>
        <p className="text-xs text-stone-400">{formatDateRange(stage.startDate, stage.endDate)}</p>
        {stage.notes && <p className="mt-1 text-sm text-stone-600">{stage.notes}</p>}
      </div>
    </li>
  )
}
