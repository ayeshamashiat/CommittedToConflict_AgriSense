import TimelineStage from './TimelineStage.jsx'
import FertilizerScheduleTable from './FertilizerScheduleTable.jsx'
import IrrigationScheduleList from './IrrigationScheduleList.jsx'
import PestRiskList from './PestRiskList.jsx'
import EmptyState from '../../components/ui/EmptyState.jsx'
import { useAppState } from '../../context/useAppState.js'

export default function SeasonTimeline() {
  const { state } = useAppState()
  const { timeline, recommendations, fertilizerSchedule, irrigationSchedule, pestRisks } = state

  if (timeline.length === 0) {
    return (
      <EmptyState
        icon="📅"
        title="No season plan yet"
        description="Once a crop is recommended, its dated calendar will appear here."
      />
    )
  }

  const cropName = recommendations[0]?.cropName ?? fertilizerSchedule?.cropName ?? irrigationSchedule?.cropName

  return (
    <div className="flex flex-col gap-6 p-4">
      {cropName && (
        <p className="text-sm text-stone-500">
          Calendar for <span className="font-semibold text-leaf-700">{cropName}</span>
        </p>
      )}
      <ol className="max-w-2xl">
        {timeline.map((stage, index) => (
          <TimelineStage key={stage.id} stage={stage} isLast={index === timeline.length - 1} />
        ))}
      </ol>
      <FertilizerScheduleTable schedule={fertilizerSchedule} />
      <IrrigationScheduleList schedule={irrigationSchedule} />
      <PestRiskList pestRisks={pestRisks} />
    </div>
  )
}
