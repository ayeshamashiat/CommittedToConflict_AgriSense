export const STORAGE_KEY = 'agrisense:v1'

export function loadState(key, fallback) {
  try {
    const raw = localStorage.getItem(key)
    if (!raw) return fallback
    const parsed = JSON.parse(raw)
    if (!parsed || typeof parsed !== 'object') return fallback
    return parsed
  } catch {
    return fallback
  }
}

export function saveState(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value))
  } catch {
    // localStorage unavailable (private browsing, quota exceeded) — persistence is best-effort
  }
}
