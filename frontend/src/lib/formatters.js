export function formatCurrencyBDT(amount) {
  if (amount == null) return '—'
  return `৳${Number(amount).toLocaleString('en-BD', { maximumFractionDigits: 0 })}`
}

export function formatPercent(value) {
  if (value == null) return '—'
  return `${Number(value).toFixed(1)}%`
}

export function formatDate(isoString) {
  if (!isoString) return '—'
  const date = new Date(isoString)
  if (Number.isNaN(date.getTime())) return isoString
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

export function formatDateRange(startIso, endIso) {
  return `${formatDate(startIso)} – ${formatDate(endIso)}`
}

export function formatTime(isoString) {
  if (!isoString) return '—'
  const date = new Date(isoString)
  if (Number.isNaN(date.getTime())) return isoString
  return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })
}
