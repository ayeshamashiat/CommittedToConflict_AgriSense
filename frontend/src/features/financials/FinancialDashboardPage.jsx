import FinancialDashboard from './FinancialDashboard.jsx'
import { useTranslation } from '../../context/useTranslation.js'

export default function FinancialDashboardPage() {
  const { t } = useTranslation()
  return (
    <div className="flex h-full flex-col overflow-y-auto">
      <h1 className="px-4 pt-4 text-2xl font-semibold text-leaf-800 sm:px-6 sm:pt-6">{t('nav_financials')}</h1>
      <FinancialDashboard />
    </div>
  )
}
