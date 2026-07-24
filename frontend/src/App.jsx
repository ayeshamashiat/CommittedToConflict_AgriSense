import { AppStateProvider } from './context/AppStateContext.jsx'
import { useAppState } from './context/useAppState.js'
import Sidebar from './app/Sidebar.jsx'
import MainHeader from './app/MainHeader.jsx'
import DashboardHome from './app/DashboardHome.jsx'
import FarmerProfilePage from './features/profile/FarmerProfilePage.jsx'
import ChatPage from './features/chat/ChatPage.jsx'
import CropRecommendationsPage from './features/crops/CropRecommendationsPage.jsx'
import SeasonPlannerPage from './features/timeline/SeasonPlannerPage.jsx'
import FinancialDashboardPage from './features/financials/FinancialDashboardPage.jsx'
import SmartAlertsPage from './features/alerts/SmartAlertsPage.jsx'
import WeatherAnalysisPage from './features/weather/WeatherAnalysisPage.jsx'
import AgentActivityPage from './features/trace/AgentActivityPage.jsx'

const SECTION_CONTENT = {
  dashboard: DashboardHome,
  profile: FarmerProfilePage,
  assistant: ChatPage,
  crops: CropRecommendationsPage,
  timeline: SeasonPlannerPage,
  financials: FinancialDashboardPage,
  alerts: SmartAlertsPage,
  weather: WeatherAnalysisPage,
  trace: AgentActivityPage,
}

function AppContent() {
  const { state } = useAppState()
  const ActiveSection = SECTION_CONTENT[state.ui.activeSection] ?? DashboardHome

  return (
    <div className="flex h-svh overflow-hidden">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
        <MainHeader />
        <main className="flex-1 overflow-hidden">
          <ActiveSection />
        </main>
      </div>
    </div>
  )
}

function App() {
  return (
    <AppStateProvider>
      <AppContent />
    </AppStateProvider>
  )
}

export default App
