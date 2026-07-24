import Badge from '../../components/ui/Badge.jsx'
import { ALERT_SEVERITY_VARIANT, ALERT_SEVERITY_ICON } from '../../lib/constants.js'

export default function AlertCard({ alert, onDismiss }) {
  return (
    <div className="rounded-lg border border-earth-100 bg-wheat-50 p-3">
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-start gap-2">
          <span className="text-lg leading-none">{ALERT_SEVERITY_ICON[alert.severity] ?? '📣'}</span>
          <div>
            <p className="text-sm font-semibold text-stone-800">{alert.title}</p>
            <p className="text-sm text-stone-600">{alert.message}</p>
          </div>
        </div>
        <Badge variant={ALERT_SEVERITY_VARIANT[alert.severity] ?? 'neutral'}>{alert.severity}</Badge>
      </div>
      <p className="mt-2 text-xs text-stone-400">{alert.reasoning}</p>
      {onDismiss && (
        <button
          type="button"
          onClick={() => onDismiss(alert.id)}
          className="mt-2 text-xs font-medium text-leaf-600 hover:underline"
        >
          Dismiss
        </button>
      )}
    </div>
  )
}
