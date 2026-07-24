import CropCard from './CropCard.jsx'
import EmptyState from '../../components/ui/EmptyState.jsx'
import { useAppState } from '../../context/useAppState.js'

export default function CropRecommendationsGrid() {
  const { state } = useAppState()
  const { recommendations } = state

  if (recommendations.length === 0) {
    return (
      <EmptyState
        icon="🌾"
        title="No recommendations yet"
        description="Send a message describing your farm to get ranked crop options."
      />
    )
  }

  return (
    <div className="grid grid-cols-1 gap-4 p-4 sm:grid-cols-2 xl:grid-cols-3">
      {recommendations.map((crop) => (
        <CropCard key={crop.id} crop={crop} />
      ))}
    </div>
  )
}
