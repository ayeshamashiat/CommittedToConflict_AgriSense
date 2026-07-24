import Badge from '../../components/ui/Badge.jsx'
import ExpandableLogItem from '../../components/ui/ExpandableLogItem.jsx'
import Spinner from '../../components/ui/Spinner.jsx'
import { TRACE_STATUS_VARIANT } from '../../lib/constants.js'
import { formatTime } from '../../lib/formatters.js'

export default function TraceEvent({ event }) {
  const summary = (
    <div className="flex min-w-0 flex-1 items-center gap-2">
      {event.status === 'pending' ? (
        <Spinner />
      ) : (
        <Badge variant={TRACE_STATUS_VARIANT[event.status] ?? 'neutral'}>{event.status}</Badge>
      )}
      <span className="truncate text-sm font-medium text-stone-800">{event.toolName}</span>
      <span className="ml-auto shrink-0 text-xs text-stone-400">
        {event.durationMs != null ? `${event.durationMs}ms` : formatTime(event.timestamp)}
      </span>
    </div>
  )

  return (
    <ExpandableLogItem summary={summary}>
      <div className="flex flex-col gap-2 text-xs">
        <div>
          <p className="mb-1 font-semibold text-stone-500">Input</p>
          <pre className="overflow-x-auto rounded-md bg-stone-50 p-2 text-stone-700">
            {JSON.stringify(event.input, null, 2)}
          </pre>
        </div>
        <div>
          <p className="mb-1 font-semibold text-stone-500">Output</p>
          <pre className="overflow-x-auto rounded-md bg-stone-50 p-2 text-stone-700">
            {JSON.stringify(event.output, null, 2)}
          </pre>
        </div>
        <p className="text-stone-400">{formatTime(event.timestamp)}</p>
      </div>
    </ExpandableLogItem>
  )
}
