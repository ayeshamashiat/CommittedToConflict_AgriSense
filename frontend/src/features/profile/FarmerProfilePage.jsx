import Tabs from '../../components/ui/Tabs.jsx'
import Button from '../../components/ui/Button.jsx'
import PersonalDetailsForm from './PersonalDetailsForm.jsx'
import FarmDetailsForm from './FarmDetailsForm.jsx'
import CurrentCropSection from './CurrentCropSection.jsx'
import LiveWeatherWidget from './LiveWeatherWidget.jsx'
import { useAppState } from '../../context/useAppState.js'
import { PROFILE_TABS } from '../../lib/constants.js'
import { clearFarmerIdentity } from '../../api/client.js'
import { STORAGE_KEY } from '../../lib/storage.js'

const TAB_CONTENT = {
  personal: PersonalDetailsForm,
  farm: FarmDetailsForm,
  crop: CurrentCropSection,
  weather: LiveWeatherWidget,
}

export default function FarmerProfilePage() {
  const { state, dispatch } = useAppState()
  const activeId = state.ui.activeProfileTab
  const ActiveContent = TAB_CONTENT[activeId]

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-4 p-4 sm:p-6">
      <div>
        <h1 className="text-2xl font-semibold text-leaf-800">Farmer Profile</h1>
        <p className="mt-1 text-sm text-stone-500">
          Ground every recommendation in your real conditions. Leave anything blank and the assistant will ask
          for it in chat.
        </p>
      </div>

      <Tabs
        tabs={PROFILE_TABS}
        activeId={activeId}
        onChange={(id) => dispatch({ type: 'SET_PROFILE_TAB', payload: id })}
      />

      <ActiveContent />

      <div className="mt-4 border-t border-earth-100 pt-4">
        <Button
          variant="ghost"
          size="sm"
          className="text-stone-400 hover:text-red-600"
          onClick={() => {
            if (
              window.confirm(
                'Reset demo? This clears the profile, chat history, generated plan, and farmer identity on this device.',
              )
            ) {
              clearFarmerIdentity()
              localStorage.removeItem(STORAGE_KEY)
              window.location.reload()
            }
          }}
        >
          Reset demo
        </Button>
      </div>
    </div>
  )
}
