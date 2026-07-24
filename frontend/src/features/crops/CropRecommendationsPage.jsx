import CropRecommendationsGrid from './CropRecommendationsGrid.jsx'

export default function CropRecommendationsPage() {
  return (
    <div className="flex h-full flex-col overflow-y-auto">
      <h1 className="px-4 pt-4 text-2xl font-semibold text-leaf-800 sm:px-6 sm:pt-6">Crop Recommendations</h1>
      <CropRecommendationsGrid />
    </div>
  )
}
