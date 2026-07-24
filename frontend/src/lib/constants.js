export const LEVEL_BADGE_VARIANT = {
  High: 'success',
  Medium: 'warning',
  Low: 'danger',
}

export const RISK_BADGE_VARIANT = {
  Low: 'success',
  Medium: 'warning',
  High: 'danger',
}

export const TRACE_STATUS_VARIANT = {
  success: 'success',
  pending: 'info',
  error: 'danger',
}

export const TIMELINE_STAGE_VARIANT = {
  completed: 'success',
  current: 'info',
  upcoming: 'neutral',
}

export const ALERT_SEVERITY_VARIANT = {
  critical: 'danger',
  warning: 'warning',
  info: 'info',
}

export const ALERT_SEVERITY_ICON = {
  critical: '⛈️',
  warning: '🌧️',
  info: '💧',
}

export const NAV_SECTIONS = [
  { id: 'dashboard', label: 'Dashboard', icon: '🏠' },
  { id: 'profile', label: 'Farmer Profile', icon: '👤' },
  { id: 'assistant', label: 'AI Assistant', icon: '💬' },
  { id: 'crops', label: 'Crop Recommendations', icon: '🌾' },
  { id: 'timeline', label: 'Season Planner', icon: '📅' },
  { id: 'financials', label: 'Financial Dashboard', icon: '💰' },
  { id: 'alerts', label: 'Smart Alerts', icon: '🔔' },
  { id: 'weather', label: 'Weather Analysis', icon: '☁️' },
  { id: 'trace', label: 'Agent Activity', icon: '🔍' },
]

export const FORM_INPUT_CLASS =
  'w-full rounded-lg border border-earth-100 bg-wheat-50 px-3 py-2 text-sm text-stone-800 outline-none focus:border-leaf-400'

export const PROFILE_TABS = [
  { id: 'personal', label: 'Personal Details' },
  { id: 'farm', label: 'Farm Details' },
  { id: 'crop', label: 'Current Crop' },
  { id: 'weather', label: 'Live Weather' },
]
