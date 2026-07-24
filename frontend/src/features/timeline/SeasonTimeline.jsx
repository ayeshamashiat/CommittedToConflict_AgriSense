import TimelineStage from './TimelineStage.jsx'
import EmptyState from '../../components/ui/EmptyState.jsx'
import { useAppState } from '../../context/useAppState.js'

export default function SeasonTimeline() {
  const { state } = useAppState()
  const { timeline } = state

  if (timeline.length === 0) {
    return (
      <EmptyState
        icon="📅"
        title="No season plan yet"
        description="Once a crop is recommended, its dated calendar will appear here."
      />
    )
  }

  return (
    <ol className="max-w-2xl p-4">
      {timeline.map((stage, index) => (
        <TimelineStage key={stage.id} stage={stage} isLast={index === timeline.length - 1} />
      ))}
    </ol>
  )
}
